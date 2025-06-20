import type { AppConfig } from "./lib/types";

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: "Botel AI",
  pageTitle: "Voice Assistant",
  pageDescription: "A voice assistant built with Botel AI",

  suportsChatInput: true,
  suportsVideoInput: true,
  suportsScreenShare: true,

  logo: "/logobotel.svg",
  accent: "#002cf2",
  logoDark: "/logobotel.svg",
  accentDark: "#1fd5f9",
  startButtonText: "Start call",
};
