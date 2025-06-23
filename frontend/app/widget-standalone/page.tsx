import { BotelWidget } from "@/components/widget/BotelWidget";

// This page is designed to be loaded in an iframe
export default async function WidgetStandalonePage({
  searchParams,
}: {
  searchParams: Promise<{
    position?: string;
    primaryColor?: string;
    companyName?: string;
  }>;
}) {
  const params = await searchParams;
  const position =
    params.position === "bottom-left" ? "bottom-left" : "bottom-right";
  const primaryColor = params.primaryColor || "#002cf2";
  const companyName = params.companyName || "Botel AI";

  return (
    <div style={{ width: "100vw", height: "100vh", background: "transparent" }}>
      <BotelWidget
        position={position}
        primaryColor={primaryColor}
        companyName={companyName}
      />
    </div>
  );
}
