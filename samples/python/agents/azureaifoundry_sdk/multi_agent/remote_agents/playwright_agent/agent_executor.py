import logging

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.types import (
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)
from a2a.utils import (
    new_agent_text_message,
    new_task,
    new_text_artifact,
)
from agent import SemanticKernelMCPAgent


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticKernelMCPAgentExecutor(AgentExecutor):
    """SemanticKernelMCPAgent Executor"""

    def __init__(self):
        self.agent = SemanticKernelMCPAgent()
        self._initialized = False

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        logger.info(f'Execute called with user input: {context.get_user_input()}')
        
        # Initialize the agent if not already done
        if not self._initialized:
            try:
                logger.info('Starting MCP Agent initialization...')
                await self.agent.initialize_playwright()
                self._initialized = True
                logger.info('MCP Agent initialized successfully')
            except Exception as e:
                logger.error(f'Failed to initialize MCP Agent: {e}')
                # Create a simple task to return error message
                task = context.current_task
                if not task:
                    task = new_task(context.message)
                    await event_queue.enqueue_event(task)
                
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        status=TaskStatus(
                            state=TaskState.failed,
                            message=new_agent_text_message(f"Failed to initialize Playwright agent: {str(e)}")
                        ),
                        task_id=task.id
                    )
                )
                return

        query = context.get_user_input()
        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
            logger.info(f'Created new task with ID: {task.id}')
        else:
            logger.info(f'Using existing task with ID: {task.id}')

        try:
            logger.info(f'Starting agent.stream for query: {query}')
            async for partial in self.agent.stream(query, task.context_id):
                logger.info(f'Received partial response: {partial}')
                require_input = partial['require_user_input']
                is_done = partial['is_task_complete']
                text_content = partial['content']

            if require_input:
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        status=TaskStatus(
                            state=TaskState.input_required,
                            message=new_agent_text_message(
                                text_content,
                                task.context_id,
                                task.id,
                            ),
                        ),
                        final=True,
                        context_id=task.context_id,
                        task_id=task.id,
                    )
                )
            elif is_done:
                await event_queue.enqueue_event(
                    TaskArtifactUpdateEvent(
                        append=False,
                        context_id=task.context_id,
                        task_id=task.id,
                        last_chunk=True,
                        artifact=new_text_artifact(
                            name='current_result',
                            description='Result of request to agent.',
                            text=text_content,
                        ),
                    )
                )
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        status=TaskStatus(state=TaskState.completed),
                        final=True,
                        context_id=task.context_id,
                        task_id=task.id,
                    )
                )
            else:
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        status=TaskStatus(
                            state=TaskState.working,
                            message=new_agent_text_message(
                                text_content,
                                task.context_id,
                                task.id,
                            ),
                        ),
                        final=False,
                        context_id=task.context_id,
                        task_id=task.id,
                    )
                )
        except Exception as e:
            logger.error(f'Error during agent execution: {e}')
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    status=TaskStatus(
                        state=TaskState.failed,
                        message=new_agent_text_message(f"Playwright agent execution failed: {str(e)}")
                    ),
                    task_id=task.id
                )
            )

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')
