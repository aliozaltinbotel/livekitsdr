"use client";

import React, { useState, useEffect, useMemo, useRef } from "react";
import { Room, RoomEvent } from "livekit-client";
import {
  RoomAudioRenderer,
  RoomContext,
  useChat,
  useTranscriptions,
  useRoomContext,
  type ReceivedChatMessage,
} from "@livekit/components-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn, transcriptionToChatMessage } from "@/lib/utils";
import useConnectionDetails from "@/hooks/useConnectionDetails";

interface BotelWidgetProps {
  position?: "bottom-right" | "bottom-left";
  primaryColor?: string;
  companyName?: string;
}

export function BotelWidget({
  position = "bottom-right",
  primaryColor = "#002cf2",
  companyName = "Botel AI",
}: BotelWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [sessionStarted, setSessionStarted] = useState(false);

  const room = useMemo(() => new Room(), []);
  const connectionDetails = useConnectionDetails();

  // Set up room event handlers
  useEffect(() => {
    const onConnected = () => setIsConnected(true);
    const onDisconnected = () => {
      setIsConnected(false);
      setSessionStarted(false);
    };

    room.on(RoomEvent.Connected, onConnected);
    room.on(RoomEvent.Disconnected, onDisconnected);

    return () => {
      room.off(RoomEvent.Connected, onConnected);
      room.off(RoomEvent.Disconnected, onDisconnected);
    };
  }, [room]);

  // Connect to room when session starts
  useEffect(() => {
    if (sessionStarted && room.state === "disconnected" && connectionDetails) {
      Promise.all([
        room.localParticipant.setMicrophoneEnabled(true, undefined, {
          preConnectBuffer: true,
        }),
        room.connect(
          connectionDetails.serverUrl,
          connectionDetails.participantToken,
        ),
      ]).catch((error) => {
        console.error("Error connecting to room:", error);
        setSessionStarted(false);
      });
    }
    return () => {
      if (sessionStarted) {
        room.disconnect();
      }
    };
  }, [room, sessionStarted, connectionDetails]);

  const toggleWidget = () => {
    setIsOpen(!isOpen);
    if (!isOpen && !sessionStarted) {
      setSessionStarted(true);
    }
  };

  const closeWidget = () => {
    setIsOpen(false);
    if (sessionStarted) {
      setSessionStarted(false);
      room.disconnect();
    }
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
              positionClasses[position],
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
              position === "bottom-right"
                ? "bottom-20 right-5"
                : "bottom-20 left-5",
              "max-[420px]:w-full max-[420px]:h-full max-[420px]:bottom-0 max-[420px]:right-0 max-[420px]:left-0 max-[420px]:rounded-none",
            )}
          >
            {/* Header */}
            <div
              className="px-5 py-4 text-white flex items-center justify-between"
              style={{ backgroundColor: primaryColor }}
            >
              <div>
                <h3 className="text-lg font-semibold">
                  {companyName} Assistant
                </h3>
                <span className="text-xs opacity-90 flex items-center">
                  <span
                    className={cn(
                      "w-2 h-2 rounded-full mr-2",
                      isConnected
                        ? "bg-green-400 animate-pulse"
                        : "bg-gray-400",
                    )}
                  />
                  {isConnected ? "Connected" : "Connecting..."}
                </span>
              </div>
              <button
                onClick={closeWidget}
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

            {/* Content Area */}
            <RoomContext.Provider value={room}>
              <RoomAudioRenderer />
              {sessionStarted ? (
                <WidgetContent
                  primaryColor={primaryColor}
                  isConnected={isConnected}
                />
              ) : (
                <div className="flex-1 flex items-center justify-center p-6">
                  <p className="text-gray-500">Initializing...</p>
                </div>
              )}
            </RoomContext.Provider>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

// Widget Content Component
function WidgetContent({
  primaryColor,
  isConnected,
}: {
  primaryColor: string;
  isConnected: boolean;
}) {
  const [inputValue, setInputValue] = useState("");
  const [isMuted, setIsMuted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const room = useRoomContext();
  const transcriptions = useTranscriptions();
  const chat = useChat();

  // Merge transcriptions and chat messages
  const messages = useMemo(() => {
    const merged: Array<ReceivedChatMessage> = [
      ...transcriptions.map((transcription) =>
        transcriptionToChatMessage(transcription, room),
      ),
      ...chat.chatMessages,
    ];
    return merged.sort((a, b) => a.timestamp - b.timestamp);
  }, [transcriptions, chat.chatMessages, room]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!inputValue.trim()) return;

    await chat.send(inputValue);
    setInputValue("");
  };

  const toggleMute = () => {
    if (room && room.localParticipant) {
      room.localParticipant.setMicrophoneEnabled(isMuted);
      setIsMuted(!isMuted);
    }
  };

  return (
    <>
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && isConnected && (
          <div className="text-center text-gray-500 mt-8">
            <p className="text-sm">Agent is listening</p>
            <p className="text-xs mt-1">Say something or type a message</p>
          </div>
        )}

        <AnimatePresence initial={false}>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className={cn(
                "flex gap-3",
                message.from?.identity === "agent" ? "" : "flex-row-reverse",
              )}
            >
              <div
                className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-medium flex-shrink-0",
                  message.from?.identity === "agent" ? "" : "bg-gray-400",
                )}
                style={{
                  backgroundColor:
                    message.from?.identity === "agent"
                      ? primaryColor
                      : undefined,
                }}
              >
                {message.from?.identity === "agent" ? "AI" : "U"}
              </div>
              <div
                className={cn(
                  "max-w-[75%] px-4 py-2.5 rounded-2xl text-sm",
                  message.from?.identity === "agent"
                    ? "bg-gray-100 text-gray-900"
                    : "bg-blue-500 text-white",
                )}
              >
                {message.message}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Input Container */}
      <div className="border-t border-gray-200 p-4">
        {/* Mic Control */}
        <div className="flex items-center justify-center mb-3">
          <button
            onClick={toggleMute}
            className={cn(
              "w-12 h-12 rounded-full flex items-center justify-center transition-all",
              isMuted
                ? "bg-gray-200 text-gray-600"
                : "bg-green-500 text-white hover:bg-green-600",
            )}
          >
            {isMuted ? (
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none">
                <path d="M11 5L6 9H2V15H6L11 19V5Z" fill="currentColor" />
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
            )}
          </button>
          <span className="ml-3 text-xs text-gray-500">
            {isMuted ? "Microphone muted" : "Microphone active"}
          </span>
        </div>

        {/* Text Input */}
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Type a message..."
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
