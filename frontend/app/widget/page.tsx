"use client";

import { BotelWidget } from "@/components/widget/BotelWidget";

export default function WidgetDemo() {
  // You can test with different configurations here
  const configs = {
    default: {
      position: "bottom-right" as const,
      primaryColor: "#002cf2",
      companyName: "Botel AI",
    },
    leftPosition: {
      position: "bottom-left" as const,
      primaryColor: "#002cf2",
      companyName: "Botel AI",
    },
    customColor: {
      position: "bottom-right" as const,
      primaryColor: "#10b981",
      companyName: "Your Company",
    },
  };

  // Change this to test different configs
  const currentConfig = configs.default;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Demo Page Content */}
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          Botel AI Widget Demo
        </h1>

        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-2xl font-semibold mb-4">Widget Preview</h2>
          <p className="text-gray-600 mb-4">
            This page demonstrates how the Botel AI widget will appear on
            customer websites. Click the chat bubble in the{" "}
            {currentConfig.position.replace("-", " ")} corner to interact with
            the widget.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            <div className="border border-gray-200 rounded p-4">
              <h3 className="font-semibold mb-2">Current Configuration:</h3>
              <pre className="text-sm bg-gray-50 p-2 rounded">
                {JSON.stringify(currentConfig, null, 2)}
              </pre>
            </div>

            <div className="border border-gray-200 rounded p-4">
              <h3 className="font-semibold mb-2">Integration Code:</h3>
              <pre className="text-xs bg-gray-50 p-2 rounded overflow-x-auto">
                {`<script>
  window.BotelWidgetConfig = ${JSON.stringify(currentConfig, null, 2)};
</script>
<script src="/widget/embed.js"></script>`}
              </pre>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4">Test Content</h2>
          <p className="text-gray-600 mb-4">
            This is example content to show how the widget overlays on top of
            your website content. The widget is positioned fixed and won&apos;t
            interfere with your page layout.
          </p>

          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="border border-gray-200 rounded p-4">
                <h3 className="font-semibold mb-2">Section {i + 1}</h3>
                <p className="text-gray-600">
                  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed
                  do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                  Ut enim ad minim veniam, quis nostrud exercitation ullamco
                  laboris.
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* The actual widget */}
      <BotelWidget {...currentConfig} />
    </div>
  );
}
