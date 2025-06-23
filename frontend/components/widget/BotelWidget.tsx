"use client";

import React, { useState, useEffect, useRef } from "react";
import { Room, RoomEvent, Track, DataPacket_Kind } from "livekit-client";
import {
  RoomAudioRenderer,
  RoomContext,
  useRoom,
  useLocalParticipant,
  useTracks,
  useDataChannel,
} from "@livekit/components-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

interface BotelWidgetProps {
  serverUrl?: string;
  token?: string;
  position?: "bottom-right" | "bottom-left";
  primaryColor?: string;
  companyName?: string;
}

export function BotelWidget({
  serverUrl,
  token,
  position = "bottom-right",
  primaryColor = "#002cf2",
  companyName = "Botel AI",
}: BotelWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [mode, setMode] = useState<"chat" | "voice">("chat");
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<
    Array<{ role: "user" | "assistant"; content: string; id: string }>
  >([
    {
      role: "assistant",
      content: "Hi! I'm Jamie from Botel AI. How can I help you today?",
      id: "initial",
    },
  ]);

  const room = useRef<Room | null>(null);

  useEffect(() => {
    // Load saved state
    const saved = localStorage.getItem("botelWidget");
    if (saved) {
      const state = JSON.parse(saved);
      if (state.isOpen) setIsOpen(true);
      if (state.mode) setMode(state.mode);
    }
  }, []);

  const saveState = () => {
    localStorage.setItem("botelWidget", JSON.stringify({ isOpen, mode }));
  };

  const toggleWidget = () => {
    setIsOpen(!isOpen);
    saveState();
  };

  const switchMode = (newMode: "chat" | "voice") => {
    setMode(newMode);
    saveState();
  };

  const positionClasses = {
    "bottom-right": "bottom-5 right-5",
    "bottom-left": "bottom-5 left-5",
  };

  return (
    <>
      {/* Widget Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            className={cn(
              "fixed z-[999998] w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-transform hover:scale-110",
              positionClasses[position]
            )}
            style={{ backgroundColor: primaryColor }}
            onClick={toggleWidget}
          >
            <svg
              className="w-7 h-7 text-white"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M12 2C6.48 2 2 6.48 2 12C2 13.19 2.23 14.32 2.64 15.36L2 22L8.64 21.36C9.68 21.77 10.81 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM17 13H15V11H17V13ZM13 13H11V11H13V13ZM9 13H7V11H9V13Z"
                fill="currentColor"
              />
            </svg>
          </motion.button>
        )}
      </AnimatePresence>

      {/* Widget Container */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className={cn(
              "fixed z-[999999] w-96 h-[600px] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden",
              position === "bottom-right" ? "bottom-20 right-5" : "bottom-20 left-5",
              "max-[420px]:w-full max-[420px]:h-full max-[420px]:bottom-0 max-[420px]:right-0 max-[420px]:left-0 max-[420px]:rounded-none"
            )}
          >
            {/* Header */}
            <div
              className="px-5 py-4 text-white flex items-center justify-between"
              style={{ backgroundColor: primaryColor }}
            >
              <div>
                <h3 className="text-lg font-semibold">{companyName} Assistant</h3>
                <span className="text-xs opacity-90 flex items-center">
                  <span className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse" />
                  Online
                </span>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 hover:opacity-80 transition-opacity"
              >
                <svg
                  className="w-6 h-6"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M18 6L6 18M6 6L18 18"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                </svg>
              </button>
            </div>

            {/* Mode Toggle */}
            <div className="flex bg-gray-100 p-1 gap-1">
              <button
                className={cn(
                  "flex-1 py-2 px-3 rounded-md text-sm font-medium transition-all flex items-center justify-center gap-2",
                  mode === "chat"
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                )}
                onClick={() => switchMode("chat")}
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M8 12H16M8 8H16M8 16H12M4 4H20C20.5523 4 21 4.44772 21 5V19C21 19.5523 20.5523 20 20 20H4C3.44772 20 3 19.5523 3 19V5C3 4.44772 3.44772 4 4 4Z"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                </svg>
                Chat
              </button>
              <button
                className={cn(
                  "flex-1 py-2 px-3 rounded-md text-sm font-medium transition-all flex items-center justify-center gap-2",
                  mode === "voice"
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                )}
                onClick={() => switchMode("voice")}
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M12 2C10.8954 2 10 2.89543 10 4V12C10 13.1046 10.8954 14 12 14C13.1046 14 14 13.1046 14 12V4C14 2.89543 13.1046 2 12 2Z"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                  <path
                    d="M17 12C17 14.7614 14.7614 17 12 17M7 12C7 14.7614 9.23858 17 12 17M12 17V21M8 21H16"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                </svg>
                Voice
              </button>
            </div>

            {/* Content Area */}
            {mode === "chat" ? (
              <ChatMode messages={messages} setMessages={setMessages} primaryColor={primaryColor} />
            ) : (
              <VoiceMode
                serverUrl={serverUrl}
                token={token}
                primaryColor={primaryColor}
                isConnected={isConnected}
                setIsConnected={setIsConnected}
              />
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

// Chat Mode Component
function ChatMode({
  messages,
  setMessages,
  primaryColor,
}: {
  messages: Array<{ role: "user" | "assistant"; content: string; id: string }>;
  setMessages: React.Dispatch<
    React.SetStateAction<
      Array<{ role: "user" | "assistant"; content: string; id: string }>
    >
  >;
  primaryColor: string;
}) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = () => {
    if (!input.trim()) return;

    const userMessage = {
      role: "user" as const,
      content: input,
      id: Date.now().toString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    // Simulate assistant response
    setTimeout(() => {
      const assistantMessage = {
        role: "assistant" as const,
        content: `I received your message: "${input}". How else can I help you?`,
        id: (Date.now() + 1).toString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    }, 1000);
  };

  return (
    <>
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence initial={false}>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className={cn("flex gap-3", message.role === "user" && "flex-row-reverse")}
            >
              <div
                className={cn(
                  "w-9 h-9 rounded-full flex items-center justify-center text-white font-medium flex-shrink-0",
                  message.role === "user" ? "bg-gray-400" : ""
                )}
                style={{
                  backgroundColor: message.role === "assistant" ? primaryColor : undefined,
                }}
              >
                {message.role === "user" ? "U" : "AI"}
              </div>
              <div
                className={cn(
                  "max-w-[70%] px-4 py-2.5 rounded-2xl",
                  message.role === "user"
                    ? "bg-gray-100 text-gray-900"
                    : "bg-gray-50 text-gray-900"
                )}
              >
                {message.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-full text-sm focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={sendMessage}
            className="w-10 h-10 rounded-full flex items-center justify-center text-white transition-colors"
            style={{ backgroundColor: primaryColor }}
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none">
              <path
                d="M22 2L11 13M22 2L15 22L11 13L2 9L22 2Z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>
      </div>
    </>
  );
}

// Voice Mode Component
function VoiceMode({
  serverUrl,
  token,
  primaryColor,
  isConnected,
  setIsConnected,
}: {
  serverUrl?: string;
  token?: string;
  primaryColor: string;
  isConnected: boolean;
  setIsConnected: React.Dispatch<React.SetStateAction<boolean>>;
}) {
  const [isMuted, setIsMuted] = useState(false);
  const [isCallActive, setIsCallActive] = useState(false);
  const [transcript, setTranscript] = useState<
    Array<{ role: "user" | "assistant"; text: string }>
  >([]);

  const roomRef = useRef<Room | null>(null);

  const startCall = async () => {
    try {
      setIsCallActive(true);
      
      if (!roomRef.current) {
        roomRef.current = new Room();
        
        // Set up event listeners
        roomRef.current.on(RoomEvent.DataReceived, (data: Uint8Array) => {
          const decoder = new TextDecoder();
          const message = JSON.parse(decoder.decode(data));
          
          if (message.type === "transcript") {
            setTranscript((prev) => [
              ...prev,
              { role: message.role, text: message.text },
            ]);
          }
        });

        roomRef.current.on(RoomEvent.Disconnected, () => {
          setIsConnected(false);
          setIsCallActive(false);
        });
      }

      // Connect to room
      if (serverUrl && token) {
        await roomRef.current.connect(serverUrl, token);
        await roomRef.current.localParticipant.setMicrophoneEnabled(true);
        setIsConnected(true);
      }
    } catch (error) {
      console.error("Error starting call:", error);
      setIsCallActive(false);
    }
  };

  const endCall = async () => {
    if (roomRef.current) {
      await roomRef.current.disconnect();
      roomRef.current = null;
    }
    setIsCallActive(false);
    setIsConnected(false);
  };

  const toggleMute = () => {
    if (roomRef.current && roomRef.current.localParticipant) {
      roomRef.current.localParticipant.setMicrophoneEnabled(isMuted);
      setIsMuted(!isMuted);
    }
  };

  return (
    <>
      {roomRef.current && (
        <RoomContext.Provider value={roomRef.current}>
          <RoomAudioRenderer />
        </RoomContext.Provider>
      )}
      
      <div className="flex-1 flex flex-col items-center justify-center p-6">
        {/* Voice Avatar */}
        <div className="relative mb-8">
          <div
            className="w-28 h-28 rounded-full flex items-center justify-center text-white text-5xl font-semibold relative z-10"
            style={{ backgroundColor: primaryColor }}
          >
            AI
          </div>
          
          {/* Speaking Animation */}
          {isCallActive && isConnected && (
            <div className="absolute inset-0 flex items-center justify-center">
              {[...Array(5)].map((_, i) => (
                <div
                  key={i}
                  className="absolute w-28 h-28 rounded-full border-2 opacity-0 animate-ping"
                  style={{
                    borderColor: primaryColor,
                    animationDelay: `${i * 0.6}s`,
                    animationDuration: "3s",
                  }}
                />
              ))}
            </div>
          )}
        </div>

        <p className="text-gray-600 mb-8">
          {!isCallActive
            ? "Click microphone to start"
            : isConnected
            ? "Connected - Speak now"
            : "Connecting..."}
        </p>

        {/* Controls */}
        <div className="flex gap-4">
          <button
            onClick={isCallActive ? endCall : startCall}
            className={cn(
              "w-14 h-14 rounded-full flex items-center justify-center text-white transition-all",
              isCallActive ? "bg-green-500 hover:bg-green-600" : ""
            )}
            style={{
              backgroundColor: !isCallActive ? primaryColor : undefined,
            }}
          >
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none">
              <path
                d="M12 2C10.8954 2 10 2.89543 10 4V12C10 13.1046 10.8954 14 12 14C13.1046 14 14 13.1046 14 12V4C14 2.89543 13.1046 2 12 2Z"
                fill="currentColor"
              />
              <path
                d="M17 12C17 14.7614 14.7614 17 12 17M7 12C7 14.7614 9.23858 17 12 17M12 17V21M8 21H16"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          </button>

          {isCallActive && (
            <>
              <button
                onClick={toggleMute}
                className="w-14 h-14 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center transition-colors"
              >
                {isMuted ? (
                  <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none">
                    <path
                      d="M11 5L6 9H2V15H6L11 19V5Z"
                      fill="currentColor"
                    />
                    <path
                      d="M23 9L17 15M17 9L23 15"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                    />
                  </svg>
                ) : (
                  <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none">
                    <path
                      d="M11 5L6 9H2V15H6L11 19V5Z"
                      fill="currentColor"
                    />
                    <path
                      d="M15.54 8.46C16.4774 9.39764 17.0039 10.6692 17.0039 11.995C17.0039 13.3208 16.4774 14.5924 15.54 15.53M19.07 4.93C20.9447 6.80528 21.9979 9.34836 21.9979 12C21.9979 14.6516 20.9447 17.1947 19.07 19.07"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                    />
                  </svg>
                )}
              </button>

              <button
                onClick={endCall}
                className="w-14 h-14 rounded-full bg-red-500 hover:bg-red-600 text-white flex items-center justify-center transition-colors"
              >
                <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M12 9C15.5 9 18.5 10.5 20.5 12.5L22 11C19.5 8.5 16 7 12 7C8 7 4.5 8.5 2 11L3.5 12.5C5.5 10.5 8.5 9 12 9ZM21 17.5C21 18.3 20.3 19 19.5 19C18.7 19 18 18.3 18 17.5V15C16 16.5 14 17 12 17C10 17 8 16.5 6 15V17.5C6 18.3 5.3 19 4.5 19C3.7 19 3 18.3 3 17.5V14.5C3 14 3.5 13.5 4 13.5C6 15 9 16 12 16C15 16 18 15 20 13.5C20.5 13.5 21 14 21 14.5V17.5Z"
                    fill="currentColor"
                  />
                </svg>
              </button>
            </>
          )}
        </div>

        {/* Transcript */}
        {transcript.length > 0 && (
          <div className="mt-8 w-full max-h-32 overflow-y-auto bg-gray-50 rounded-lg p-4">
            <div className="text-xs font-semibold text-gray-500 mb-2">
              CONVERSATION
            </div>
            {transcript.map((entry, i) => (
              <div
                key={i}
                className={cn(
                  "text-sm mb-1",
                  entry.role === "user" ? "text-blue-600" : "text-gray-700"
                )}
              >
                {entry.role === "user" ? "You: " : "Agent: "}
                {entry.text}
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}