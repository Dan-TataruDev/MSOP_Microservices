import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { apiServices } from '../stores/authStore';
import { Button } from '@hospitality-platform/design-system';
import { formatCurrency } from '@hospitality-platform/utils';

export default function OrderPage() {
  const { venueId } = useParams<{ venueId: string }>();
  const navigate = useNavigate();
  const [cart, setCart] = useState<Array<{ productId: string; quantity: number }>>([]);

  const { data: venue } = useQuery({
    queryKey: ['venue', venueId],
    queryFn: async () => {
      if (!venueId) throw new Error('Venue ID is required');
      const response = await apiServices.venues.getById(venueId);
      return response.data;
    },
    enabled: !!venueId,
  });

  const orderMutation = useMutation({
    mutationFn: async () => {
      if (!venueId) throw new Error('Venue ID is required');
      if (cart.length === 0) throw new Error('Cart is empty');
      return apiServices.orders.create({
        venueId,
        items: cart,
      });
    },
    onSuccess: () => {
      navigate('/profile');
    },
  });

  const addToCart = (productId: string) => {
    setCart((prev) => {
      const existing = prev.find((item) => item.productId === productId);
      if (existing) {
        return prev.map((item) =>
          item.productId === productId ? { ...item, quantity: item.quantity + 1 } : item
        );
      }
      return [...prev, { productId, quantity: 1 }];
    });
  };

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Place an Order</h1>
        {venue && <p className="text-gray-600 mb-6">Ordering from {venue.name}</p>}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600">Product catalog would be displayed here</p>
              <p className="text-sm text-gray-500 mt-2">
                This is a placeholder. In a full implementation, you would fetch products from the venue and display them here.
              </p>
            </div>
          </div>
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Cart</h2>
              {cart.length === 0 ? (
                <p className="text-gray-500">Your cart is empty</p>
              ) : (
                <div className="space-y-2">
                  {cart.map((item) => (
                    <div key={item.productId} className="flex justify-between">
                      <span>Item {item.productId}</span>
                      <span>Qty: {item.quantity}</span>
                    </div>
                  ))}
                  <Button
                    fullWidth
                    onClick={() => orderMutation.mutate()}
                    isLoading={orderMutation.isPending}
                    className="mt-4"
                  >
                    Place Order
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

