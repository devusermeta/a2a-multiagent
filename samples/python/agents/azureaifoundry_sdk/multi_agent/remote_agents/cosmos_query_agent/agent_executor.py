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
from agent import CosmosQueryAgent


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CosmosQueryAgentExecutor(AgentExecutor):
    """Cosmos Query Agent Executor using Azure Cosmos DB MCP Server"""

    def __init__(self):
        self.agent = CosmosQueryAgent()
        self._initialized = False

    async def execute(
        self, request_context: RequestContext, event_queue: EventQueue
    ) -> None:
        """
        Execute a task using the Cosmos Query Agent.
        
        Args:
            request_context: The request context containing the task
            event_queue: The event queue for status updates
        """
        try:
            # Initialize agent if needed
            if not self._initialized:
                logger.info("Initializing Cosmos Query Agent...")
                success = await self.agent.initialize()
                if not success:
                    await self._send_error(
                        request_context, event_queue, "Failed to initialize Cosmos Query Agent"
                    )
                    return
                self._initialized = True
                logger.info("Cosmos Query Agent initialized successfully")

            # Get the user query from the task
            task = request_context.task
            user_query = task.description
            
            # Send status update
            await event_queue.enqueue(
                TaskStatusUpdateEvent(
                    task_id=task.id,
                    status=TaskStatus.IN_PROGRESS,
                    state=TaskState.RUNNING,
                    message="Processing Cosmos DB query...",
                )
            )

            logger.info(f"Cosmos Query Agent executing task: {task.id}")
            logger.info(f"User query: {user_query}")
            
            # Process the query using the Cosmos Query Agent
            response = await self.agent.process_query(user_query)
            
            # Create text artifact with the response
            text_artifact = new_text_artifact(
                task_id=task.id,
                content=response,
                title="Cosmos DB Query Result"
            )

            # Send artifact update
            await event_queue.enqueue(
                TaskArtifactUpdateEvent(
                    task_id=task.id,
                    artifact=text_artifact,
                )
            )

            # Send completion status
            await event_queue.enqueue(
                TaskStatusUpdateEvent(
                    task_id=task.id,
                    status=TaskStatus.COMPLETED,
                    state=TaskState.COMPLETED,
                    message="Cosmos DB query completed successfully",
                )
            )

            logger.info(f"Cosmos Query Agent successfully processed query: {user_query}")
            
        except Exception as e:
            logger.error(f"Error in Cosmos Query Agent execution: {e}")
            await self._send_error(
                request_context, 
                event_queue, 
                f"Error executing Cosmos Query Agent task: {str(e)}"
            )

    async def _send_error(
        self, request_context: RequestContext, event_queue: EventQueue, error_message: str
    ):
        """Send error status and artifact."""
        task = request_context.task
        
        # Create error artifact
        error_artifact = new_text_artifact(
            task_id=task.id,
            content=f"Sorry, I encountered an error while querying the Cosmos DB: {error_message}",
            title="Error"
        )

        # Send error artifact
        await event_queue.enqueue(
            TaskArtifactUpdateEvent(
                task_id=task.id,
                artifact=error_artifact,
            )
        )

        # Send error status
        await event_queue.enqueue(
            TaskStatusUpdateEvent(
                task_id=task.id,
                status=TaskStatus.FAILED,
                state=TaskState.FAILED,
                message=error_message,
            )
        )

    async def cancel(
        self, request_context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Cancel the current task execution."""
        logger.info("Cosmos Query Agent task cancelled")
        raise Exception('Cosmos Query Agent task was cancelled')
