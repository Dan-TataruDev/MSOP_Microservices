import { Building2, Plus, Mail, Calendar, MapPin, CheckCircle, XCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

const MOCK_BUSINESSES = [
  { id: 1, name: 'Grand Hotel Downtown', email: 'contact@grandhotel.com', location: 'New York, NY', status: 'verified', revenue: 125000, bookings: 450, createdAt: '2024-01-10' },
  { id: 2, name: 'Beachside Resort', email: 'info@beachside.com', location: 'Miami, FL', status: 'verified', revenue: 98000, bookings: 320, createdAt: '2024-01-25' },
  { id: 3, name: 'Mountain View Lodge', email: 'hello@mountainview.com', location: 'Denver, CO', status: 'pending', revenue: 45000, bookings: 180, createdAt: '2024-02-15' },
  { id: 4, name: 'City Center Hotel', email: 'contact@citycenter.com', location: 'Chicago, IL', status: 'verified', revenue: 156000, bookings: 520, createdAt: '2024-01-05' },
  { id: 5, name: 'Riverside Inn', email: 'info@riverside.com', location: 'Portland, OR', status: 'verified', revenue: 78000, bookings: 290, createdAt: '2024-02-01' },
  { id: 6, name: 'Sunset Motel', email: 'hello@sunset.com', location: 'Los Angeles, CA', status: 'pending', revenue: 32000, bookings: 120, createdAt: '2024-03-01' },
  { id: 7, name: 'Historic Manor', email: 'contact@historic.com', location: 'Boston, MA', status: 'verified', revenue: 112000, bookings: 380, createdAt: '2024-01-20' },
  { id: 8, name: 'Lakeside Retreat', email: 'info@lakeside.com', location: 'Seattle, WA', status: 'verified', revenue: 89000, bookings: 310, createdAt: '2024-02-10' },
];

export default function BusinessesPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Business Management</h1>
          <p className="text-slate-600">Manage business accounts and verifications</p>
        </div>
        <Button leftIcon={<Plus className="w-4 h-4" />}>
          Add Business
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Total Businesses</p>
                <p className="text-3xl font-bold text-slate-900">{MOCK_BUSINESSES.length}</p>
              </div>
              <Building2 className="w-12 h-12 text-blue-500 opacity-20" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Verified</p>
                <p className="text-3xl font-bold text-green-600">{MOCK_BUSINESSES.filter(b => b.status === 'verified').length}</p>
              </div>
              <CheckCircle className="w-12 h-12 text-green-500 opacity-20" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Pending</p>
                <p className="text-3xl font-bold text-yellow-600">{MOCK_BUSINESSES.filter(b => b.status === 'pending').length}</p>
              </div>
              <XCircle className="w-12 h-12 text-yellow-500 opacity-20" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Total Revenue</p>
                <p className="text-3xl font-bold text-purple-600">
                  ${(MOCK_BUSINESSES.reduce((sum, b) => sum + b.revenue, 0) / 1000).toFixed(0)}K
                </p>
              </div>
              <Building2 className="w-12 h-12 text-purple-500 opacity-20" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Building2 className="w-5 h-5 mr-2" />
            All Businesses
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-6">
            <Input
              placeholder="Search businesses..."
              leftIcon={<Building2 className="w-4 h-4" />}
            />
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Business Name</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Contact</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Location</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Status</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Revenue</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Bookings</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Joined</th>
                </tr>
              </thead>
              <tbody>
                {MOCK_BUSINESSES.map((business) => (
                  <tr key={business.id} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="py-4 px-4">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-red-500 rounded-lg flex items-center justify-center text-white font-semibold">
                          {business.name.charAt(0)}
                        </div>
                        <span className="ml-3 font-medium text-slate-900">{business.name}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center text-slate-600">
                        <Mail className="w-4 h-4 mr-2" />
                        {business.email}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center text-slate-600">
                        <MapPin className="w-4 h-4 mr-2" />
                        {business.location}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        business.status === 'verified' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                      }`}>
                        {business.status}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <span className="font-semibold text-slate-900">${business.revenue.toLocaleString()}</span>
                    </td>
                    <td className="py-4 px-4 text-slate-900 font-medium">{business.bookings}</td>
                    <td className="py-4 px-4">
                      <div className="flex items-center text-slate-600 text-sm">
                        <Calendar className="w-4 h-4 mr-2" />
                        {new Date(business.createdAt).toLocaleDateString()}
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

