import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { apiServices } from '../stores/authStore';
import { Button } from '@hospitality-platform/design-system';

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
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-6">
          <h1 className="text-2xl font-bold mb-6">Make a Booking</h1>
          {venue && <p className="text-gray-600 mb-6">Booking at {venue.name}</p>}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-1">
                Date
              </label>
              <input
                id="date"
                type="date"
                value={formData.date}
                onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                min={new Date().toISOString().split('T')[0]}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label htmlFor="time" className="block text-sm font-medium text-gray-700 mb-1">
                Time
              </label>
              <input
                id="time"
                type="time"
                value={formData.time}
                onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label htmlFor="partySize" className="block text-sm font-medium text-gray-700 mb-1">
                Party Size
              </label>
              <input
                id="partySize"
                type="number"
                min="1"
                max="20"
                value={formData.partySize}
                onChange={(e) => setFormData({ ...formData, partySize: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label htmlFor="specialRequests" className="block text-sm font-medium text-gray-700 mb-1">
                Special Requests (Optional)
              </label>
              <textarea
                id="specialRequests"
                value={formData.specialRequests}
                onChange={(e) => setFormData({ ...formData, specialRequests: e.target.value })}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <Button type="submit" fullWidth isLoading={bookingMutation.isPending}>
              Confirm Booking
            </Button>
          </form>
        </div>
      </div>
    </Layout>
  );
}

