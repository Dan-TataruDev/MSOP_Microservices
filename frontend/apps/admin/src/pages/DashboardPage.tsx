export default function DashboardPage() {
  return (
    <div className="container mx-auto px-4">
      <h1 className="text-3xl font-bold mb-6">Admin Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Total Users</h3>
          <p className="text-2xl font-bold">-</p>
          <p className="text-sm text-gray-600 mt-1">System-wide</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Total Businesses</h3>
          <p className="text-2xl font-bold">-</p>
          <p className="text-sm text-gray-600 mt-1">Active businesses</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">System Health</h3>
          <p className="text-2xl font-bold text-green-600">Healthy</p>
          <p className="text-sm text-gray-600 mt-1">All systems operational</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
        <p className="text-gray-500">Activity logs will be displayed here</p>
      </div>
    </div>
  );
}

