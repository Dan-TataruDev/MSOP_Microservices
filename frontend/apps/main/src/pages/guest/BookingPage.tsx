import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Calendar, Clock, Users, MessageSquare } from 'lucide-react';
import { apiServices } from '@/stores/authStore';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

export default function BookingPage() {
  const { venueId } = useParams<{ venueId: string }>();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    date: '',
    time: '',
    partySize: 2,
    specialRequests: '',
  });

  const { data: venue } = useQuery({
    queryKey: ['venue', venueId],
    queryFn: async () => {
      if (!venueId) throw new Error('Venue ID is required');
      const response = await apiServices.venues.getById(venueId);
      return response.data;
    },
    enabled: !!venueId,
  });

  const bookingMutation = useMutation({
    mutationFn: async () => {
      if (!venueId) throw new Error('Venue ID is required');
      return apiServices.bookings.create({
        venueId,
        date: formData.date,
        time: formData.time,
        partySize: formData.partySize,
        specialRequests: formData.specialRequests || undefined,
      });
    },
    onSuccess: () => {
      navigate('/profile');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    bookingMutation.mutate();
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>Make a Booking</CardTitle>
          {venue && <p className="text-slate-600 mt-2">Booking at {venue.name}</p>}
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
              label="Date"
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              min={new Date().toISOString().split('T')[0]}
              leftIcon={<Calendar className="w-4 h-4" />}
              required
            />
            <Input
              label="Time"
              type="time"
              value={formData.time}
              onChange={(e) => setFormData({ ...formData, time: e.target.value })}
              leftIcon={<Clock className="w-4 h-4" />}
              required
            />
            <Input
              label="Party Size"
              type="number"
              min="1"
              max="20"
              value={formData.partySize}
              onChange={(e) => setFormData({ ...formData, partySize: parseInt(e.target.value) })}
              leftIcon={<Users className="w-4 h-4" />}
              required
            />
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                <MessageSquare className="w-4 h-4 inline mr-2" />
                Special Requests (Optional)
              </label>
              <textarea
                value={formData.specialRequests}
                onChange={(e) => setFormData({ ...formData, specialRequests: e.target.value })}
                rows={4}
                className="w-full px-4 py-3 rounded-xl border border-slate-200 bg-white/80 backdrop-blur-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
              />
            </div>
            <Button type="submit" fullWidth isLoading={bookingMutation.isPending}>
              Confirm Booking
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

