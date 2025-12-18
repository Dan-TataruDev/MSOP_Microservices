import { Users, Plus, Mail, Calendar, Shield } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

const MOCK_USERS = [
  { id: 1, name: 'John Doe', email: 'john.doe@example.com', role: 'guest', status: 'active', createdAt: '2024-01-15', bookings: 12 },
  { id: 2, name: 'Jane Smith', email: 'jane.smith@example.com', role: 'business', status: 'active', createdAt: '2024-02-20', bookings: 45 },
  { id: 3, name: 'Admin User', email: 'admin@example.com', role: 'admin', status: 'active', createdAt: '2024-01-01', bookings: 0 },
  { id: 4, name: 'Mike Johnson', email: 'mike.j@example.com', role: 'guest', status: 'active', createdAt: '2024-03-10', bookings: 8 },
  { id: 5, name: 'Sarah Williams', email: 'sarah.w@example.com', role: 'business', status: 'active', createdAt: '2024-02-05', bookings: 32 },
  { id: 6, name: 'David Brown', email: 'david.b@example.com', role: 'guest', status: 'inactive', createdAt: '2024-01-25', bookings: 3 },
  { id: 7, name: 'Emily Davis', email: 'emily.d@example.com', role: 'guest', status: 'active', createdAt: '2024-03-15', bookings: 15 },
  { id: 8, name: 'Robert Miller', email: 'robert.m@example.com', role: 'business', status: 'active', createdAt: '2024-02-12', bookings: 28 },
];

export default function UsersPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">User Management</h1>
          <p className="text-slate-600">Manage platform users and permissions</p>
        </div>
        <Button leftIcon={<Plus className="w-4 h-4" />}>
          Add User
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Total Users</p>
                <p className="text-3xl font-bold text-slate-900">{MOCK_USERS.length}</p>
              </div>
              <Users className="w-12 h-12 text-blue-500 opacity-20" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Active Users</p>
                <p className="text-3xl font-bold text-green-600">{MOCK_USERS.filter(u => u.status === 'active').length}</p>
              </div>
              <Shield className="w-12 h-12 text-green-500 opacity-20" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Business Accounts</p>
                <p className="text-3xl font-bold text-purple-600">{MOCK_USERS.filter(u => u.role === 'business').length}</p>
              </div>
              <Shield className="w-12 h-12 text-purple-500 opacity-20" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Users className="w-5 h-5 mr-2" />
            All Users
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-6">
            <Input
              placeholder="Search users..."
              leftIcon={<Users className="w-4 h-4" />}
            />
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Name</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Email</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Role</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Status</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Bookings</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Joined</th>
                </tr>
              </thead>
              <tbody>
                {MOCK_USERS.map((user) => (
                  <tr key={user.id} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="py-4 px-4">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-semibold">
                          {user.name.charAt(0)}
                        </div>
                        <span className="ml-3 font-medium text-slate-900">{user.name}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center text-slate-600">
                        <Mail className="w-4 h-4 mr-2" />
                        {user.email}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        user.role === 'admin' ? 'bg-red-100 text-red-700' :
                        user.role === 'business' ? 'bg-purple-100 text-purple-700' :
                        'bg-blue-100 text-blue-700'
                      }`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        user.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                      }`}>
                        {user.status}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-slate-900 font-medium">{user.bookings}</td>
                    <td className="py-4 px-4">
                      <div className="flex items-center text-slate-600 text-sm">
                        <Calendar className="w-4 h-4 mr-2" />
                        {new Date(user.createdAt).toLocaleDateString()}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

