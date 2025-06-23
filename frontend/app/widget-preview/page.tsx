import { BotelWidget } from "@/components/widget/BotelWidget";

export default function WidgetPreviewPage() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          Botel AI Widget Preview
        </h1>

        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-2xl font-semibold mb-4">How it works</h2>
          <ul className="space-y-2 text-gray-600">
            <li>• Click the chat button in the bottom-right corner</li>
            <li>• The widget connects to your LiveKit agent automatically</li>
            <li>• Speak or type messages - both work seamlessly</li>
            <li>• Voice is automatically transcribed to text</li>
            <li>• Agent responses appear in real-time</li>
          </ul>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4">Integration</h2>
          <p className="text-gray-600 mb-4">
            To integrate this widget on any website, add the following code:
          </p>
          <pre className="bg-gray-50 p-4 rounded overflow-x-auto text-sm">
            {`<script>
  window.BotelWidgetConfig = {
    position: 'bottom-right',
    primaryColor: '#002cf2',
    companyName: 'Your Company'
  };
</script>
<script src="https://your-domain.com/widget/embed.js"></script>`}
          </pre>
        </div>
      </div>

      {/* The actual widget */}
      <BotelWidget />
    </div>
  );
}
