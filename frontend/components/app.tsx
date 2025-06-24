"use client";

import * as React from "react";
import { Room, RoomEvent } from "livekit-client";
import { motion } from "motion/react";
import {
  RoomAudioRenderer,
  RoomContext,
  StartAudio,
} from "@livekit/components-react";
import { toastAlert } from "@/components/alert-toast";
import { SessionView } from "@/components/session-view";
import { Toaster } from "@/components/ui/sonner";
import { Welcome } from "@/components/welcome";
import useConnectionDetails from "@/hooks/useConnectionDetails";
import type { AppConfig } from "@/lib/types";

const MotionSessionView = motion.create(SessionView);
const MotionWelcome = motion.create(Welcome);

interface AppProps {
  appConfig: AppConfig;
}

export function App({ appConfig }: AppProps) {
  const [sessionStarted, setSessionStarted] = React.useState(false);
  const {
    suportsChatInput,
    suportsVideoInput,
    suportsScreenShare,
    startButtonText,
  } = appConfig;

  const capabilities = {
    suportsChatInput,
    suportsVideoInput,
    suportsScreenShare,
  };

  const connectionDetails = useConnectionDetails();

  React.useEffect(() => {
    if (connectionDetails) {
      console.log("[App] Connection details received:", {
        serverUrl: connectionDetails.serverUrl,
        roomName: connectionDetails.roomName,
        participantName: connectionDetails.participantName,
      });
    }
  }, [connectionDetails]);

  const room = React.useMemo(() => new Room(), []);

  React.useEffect(() => {
    const onDisconnected = () => {
      console.log("[App] Room disconnected");
      setSessionStarted(false);
    };
    const onMediaDevicesError = (error: Error) => {
      console.error("[App] Media devices error:", error);
      toastAlert({
        title: "Encountered an error with your media devices",
        description: `${error.name}: ${error.message}`,
      });
    };
    const onConnected = () => {
      console.log("[App] Room connected successfully");
    };
    const onConnectionStateChanged = (state: string) => {
      console.log("[App] Room connection state changed:", state);
    };
    const onParticipantConnected = (participant: { identity: string }) => {
      console.log("[App] Participant connected:", participant);
    };

    room.on(RoomEvent.MediaDevicesError, onMediaDevicesError);
    room.on(RoomEvent.Disconnected, onDisconnected);
    room.on(RoomEvent.Connected, onConnected);
    room.on(RoomEvent.ConnectionStateChanged, onConnectionStateChanged);
    room.on(RoomEvent.ParticipantConnected, onParticipantConnected);

    return () => {
      room.off(RoomEvent.Disconnected, onDisconnected);
      room.off(RoomEvent.MediaDevicesError, onMediaDevicesError);
      room.off(RoomEvent.Connected, onConnected);
      room.off(RoomEvent.ConnectionStateChanged, onConnectionStateChanged);
      room.off(RoomEvent.ParticipantConnected, onParticipantConnected);
    };
  }, [room]);

  React.useEffect(() => {
    if (sessionStarted && room.state === "disconnected" && connectionDetails) {
      console.log("[App] Starting session with:", {
        roomState: room.state,
        serverUrl: connectionDetails.serverUrl,
        roomName: connectionDetails.roomName,
      });

      Promise.all([
        room.localParticipant.setMicrophoneEnabled(true, undefined, {
          preConnectBuffer: true,
        }),
        room.connect(
          connectionDetails.serverUrl,
          connectionDetails.participantToken,
        ),
      ])
        .then(() => {
          console.log("[App] Room connection initiated successfully");
        })
        .catch((error) => {
          console.error("[App] Error connecting to room:", error);
          toastAlert({
            title: "There was an error connecting to the agent",
            description: `${error.name}: ${error.message}`,
          });
        });
    }
    return () => {
      if (room.state !== "disconnected") {
        console.log("[App] Disconnecting from room");
        room.disconnect();
      }
    };
  }, [room, sessionStarted, connectionDetails]);

  return (
    <>
      <MotionWelcome
        key="welcome"
        startButtonText={startButtonText}
        onStartCall={() => setSessionStarted(true)}
        disabled={sessionStarted}
        initial={{ opacity: 0 }}
        animate={{ opacity: sessionStarted ? 0 : 1 }}
        transition={{
          duration: 0.5,
          ease: "linear",
          delay: sessionStarted ? 0 : 0.5,
        }}
      />

      <RoomContext.Provider value={room}>
        <RoomAudioRenderer />
        <StartAudio label="Start Audio" />
        {/* --- */}
        <MotionSessionView
          key="session-view"
          capabilities={capabilities}
          sessionStarted={sessionStarted}
          disabled={!sessionStarted}
          initial={{ opacity: 0 }}
          animate={{ opacity: sessionStarted ? 1 : 0 }}
          transition={{
            duration: 0.5,
            ease: "linear",
            delay: sessionStarted ? 0.5 : 0,
          }}
        />
      </RoomContext.Provider>

      <Toaster />
    </>
  );
}
