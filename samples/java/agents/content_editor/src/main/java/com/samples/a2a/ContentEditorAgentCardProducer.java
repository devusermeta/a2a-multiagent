package com.samples.a2a;

import io.a2a.server.PublicAgentCard;
import io.a2a.spec.AgentCapabilities;
import io.a2a.spec.AgentCard;
import io.a2a.spec.AgentSkill;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.inject.Produces;
import jakarta.inject.Inject;
import org.eclipse.microprofile.config.inject.ConfigProperty;

import java.util.Collections;
import java.util.List;

/**
 * Producer for content editor agent card configuration.
 * This class is final and not designed for extension.
 */
@ApplicationScoped
public final class ContentEditorAgentCardProducer {

    /**
     * The HTTP port for the agent service.
     */
    @Inject
    @ConfigProperty(name = "quarkus.http.port")
    private int httpPort;

    /**
     * Gets the HTTP port.
     *
     * @return the HTTP port
     */
    public int getHttpPort() {
        return httpPort;
    }

    /**
     * Produces the agent card for the content editor agent.
     *
     * @return the configured agent card
     */
    @Produces
    @PublicAgentCard
    public AgentCard agentCard() {
        return new AgentCard.Builder()
                .name("Content Editor Agent")
                .description(
                        "An agent that can proof-read and polish content.")
                .url("http://localhost:" + getHttpPort())
                .version("1.0.0")
                .documentationUrl("http://example.com/docs")
                .capabilities(new AgentCapabilities.Builder()
                        .streaming(true)
                        .pushNotifications(false)
                        .stateTransitionHistory(false)
                        .build())
                .defaultInputModes(Collections.singletonList("text"))
                .defaultOutputModes(Collections.singletonList("text"))
                .skills(Collections.singletonList(new AgentSkill.Builder()
                        .id("editor")
                        .name("Edits content")
                        .description(
                                "Edits content by proof-reading and polishing")
                        .tags(List.of("writer"))
                        .examples(List.of(
                                "Edit the following article, make sure it has "
                                        + "a professional tone"))
                        .build()))
                .protocolVersion("0.2.5")
                .build();
    }
}
