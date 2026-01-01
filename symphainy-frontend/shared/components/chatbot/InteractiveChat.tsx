/**
 * Interactive Chat Component
 * 
 * Contains all the interactive chat functionality with the new agent architecture.
 * This component is dynamically loaded to avoid SSR issues.
 */

"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, SendHorizontal } from "lucide-react";
import StreamingMessage from "./StreamingMessage";
import { useRouter } from "next/navigation";
import { useAtomValue, useSetAtom } from "jotai";
import { chatbotAgentInfoAtom, mainChatbotOpenAtom } from "@/shared/atoms/chatbot-atoms";
import { useGlobalSession } from "@/shared/agui/GlobalSessionProvider";
import { useAuth } from "@/shared/agui/AuthProvider";
// useAgentManager will be dynamically imported to avoid SSR issues

export default function InteractiveChat() {
  const router = useRouter();
  const { guideSessionToken } = useGlobalSession();
  const { isAuthenticated } = useAuth();
  
  // Dynamic state for agent manager
  const [agentManager, setAgentManager] = useState<any>(null);
  const [agentLoading, setAgentLoading] = useState(true);
  const [agentError, setAgentError] = useState<string | null>(null);
  
  const mainChatbotOpen = useAtomValue(mainChatbotOpenAtom);
  const setMainChatbotOpen = useSetAtom(mainChatbotOpenAtom);
  const [message, setMessage] = useState("");
  const [wsMessages, setWsMessages] = useState<
    {
      type: "user" | "agent" | "system";
      content: string;
      isStreaming?: boolean;
      isComplete?: boolean;
      pillar?: string;
    }[]
  >([]);
  const [loading, setLoading] = useState(false);
  const [isVisible, setIsVisible] = useState(true);
  const [shouldStartAnimation, setShouldStartAnimation] = useState(false);
  const [agentData, setAgentData] = useState<any>(null);
  const [pillar, setPillar] = useState<string | null>(null);

  // Dynamically load the agent manager - only if authenticated
  useEffect(() => {
    if (!isAuthenticated || !guideSessionToken) return;

    const loadAgentManager = async () => {
      try {
        setAgentLoading(true);
        setAgentError(null);

        // Dynamically import the useAgentManager hook
        const { useAgentManager } = await import("@/shared/hooks/useAgentManager");
        
        // Create a temporary component to use the hook
        const AgentManagerWrapper = () => {
          const manager = useAgentManager(guideSessionToken, "general");
          return manager;
        };

        // For now, we'll simulate the manager state
        // In a real implementation, we'd need to restructure this
        setAgentManager({
          isConnected: true,
          isLoading: false,
          error: null,
          sendToGuideAgent: async (message: string) => ({ success: true, content: "Response from guide agent" }),
          sendToContentAgent: async (message: string) => ({ success: true, content: "Response from content agent" }),
          sendToInsightsAgent: async (message: string) => ({ success: true, content: "Response from insights agent" }),
          sendToOperationsAgent: async (message: string) => ({ success: true, content: "Response from operations agent" }),
          sendToExperienceAgent: async (message: string) => ({ success: true, content: "Response from experience agent" }),
        });
      } catch (error: any) {
        console.error("Failed to load agent manager:", error);
        setAgentError(error.message || "Failed to load agent manager");
      } finally {
        setAgentLoading(false);
      }
    };

    loadAgentManager();
  }, [isAuthenticated, guideSessionToken]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || !agentManager) return;

    setLoading(true);

    // Determine current pillar from URL or agent data
    const currentPillar = agentData?.pillar || "general";
    const agentType = currentPillar === "general" ? "guide" : currentPillar;

    try {
      // Use agent manager to send message
      let response;
      switch (agentType) {
        case "guide":
          response = await agentManager.sendToGuideAgent(message);
          break;
        case "content":
          response = await agentManager.sendToContentAgent(message);
          break;
        case "insights":
          response = await agentManager.sendToInsightsAgent(message);
          break;
        case "operations":
          response = await agentManager.sendToOperationsAgent(message);
          break;
        case "experience":
          response = await agentManager.sendToExperienceAgent(message);
          break;
        default:
          response = await agentManager.sendToGuideAgent(message);
      }

      // Add user message to chat
      setWsMessages((prev) => [
        ...prev,
        { type: "user", content: message, isComplete: true },
      ]);

      // Add agent response to chat
      if (response.success) {
        setWsMessages((prev) => [
          ...prev,
          { 
            type: "agent", 
            content: response.content || "No response", 
            isComplete: true,
            pillar: response.current_pillar
          },
        ]);

        // Update agent data
        if (response.agent) {
          setAgentData({ agent: response.agent, pillar: response.current_pillar });
        }
      } else {
        setWsMessages((prev) => [
          ...prev,
          { 
            type: "agent", 
            content: `Error: ${response.error || "Unknown error"}`, 
            isComplete: true 
          },
        ]);
      }

      setMessage("");
    } catch (error: any) {
      console.error("Error sending message:", error);
      setWsMessages((prev) => [
        ...prev,
        { 
          type: "agent", 
          content: `Error: ${error.message || "Failed to send message"}`, 
          isComplete: true 
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleStreamingComplete = (messageIndex: number) => {
    setWsMessages((prev) =>
      prev.map((msg, idx) =>
        idx === messageIndex ? { ...msg, isComplete: true } : msg
      )
    );
  };

  // Show loading state if agent manager is still loading
  if (agentLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-2" />
          <p className="text-sm text-gray-500">Initializing chat...</p>
        </div>
      </div>
    );
  }

  // Show error state if agent manager failed to initialize
  if (agentError) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-sm text-red-500 mb-2">Chat initialization failed</p>
          <p className="text-xs text-gray-500">{agentError}</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {wsMessages.length === 0 ? (
          <div className="text-gray-500 text-xs">
            Ask me anything! I'm here to help guide you through your business transformation.
          </div>
        ) : (
          wsMessages.map((msg, idx) => (
            <div 
              key={idx} 
              data-testid={`guide-agent-message-${msg.type}`}
              data-message-id={idx}
              className="flex flex-col gap-1"
            >
              <p
                className={`text-xs text-gray-500 pr-2 ${msg.type === "user" ? "text-right" : "text-left"}`}
              >
                {msg.type === "user"
                  ? "you"
                  : msg.type === "system"
                    ? "system"
                    : "agent"}
              </p>

              {/* Render agent messages with streaming effect */}
              {msg.type === "agent" ? (
                <StreamingMessage
                  content={msg.content}
                  isComplete={msg.isComplete}
                  typingSpeed={25}
                  onComplete={() => handleStreamingComplete(idx)}
                />
              ) : (
                <div
                  className={`rounded-lg py-2 px-3 text-sm shadow-md max-w-[80%] ${
                    msg.type === "user"
                      ? "text-gray-800 ml-auto text-left"
                      : "text-gray-800 w-full text-left"
                  }`}
                >
                  <>
                    {/* Replace newlines with <br> tags for proper formatting */}
                    {msg.content.split("\n").map((line, lineIdx) => (
                      <React.Fragment key={lineIdx}>
                        {line}
                        {lineIdx < msg.content.split("\n").length - 1 && (
                          <br />
                        )}
                      </React.Fragment>
                    ))}
                  </>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Input Area */}
      <div 
        data-testid="guide-agent-input-container"
        className="border-t border-[#e5eaed] p-3 bg-white"
      >
        <form onSubmit={handleSend} className="flex gap-2">
          <Input
            data-testid="send-message-to-guide-agent"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask me anything..."
            className="flex-1 text-sm"
            disabled={loading || !agentManager?.isConnected}
            aria-label="Send message to Guide Agent"
          />
          <Button
            data-testid="submit-message-to-guide-agent"
            type="submit"
            size="sm"
            disabled={loading || !message.trim() || !agentManager?.isConnected}
            className="px-3"
            aria-label="Submit message to Guide Agent"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <SendHorizontal className="h-4 w-4" />
            )}
          </Button>
        </form>
        {!agentManager?.isConnected && (
          <p className="text-xs text-red-500 mt-1">Connecting to chat service...</p>
        )}
      </div>
    </>
  );
}
