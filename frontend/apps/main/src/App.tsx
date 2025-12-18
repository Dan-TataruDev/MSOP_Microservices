import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './stores/authStore';
import RootLayout from './components/layouts/RootLayout';
import GuestLayout from './components/layouts/GuestLayout';
import BusinessLayout from './components/layouts/BusinessLayout';
import AdminLayout from './components/layouts/AdminLayout';

// Guest pages
import HomePage from './pages/guest/HomePage';
import SearchPage from './pages/guest/SearchPage';
import VenueDetailPage from './pages/guest/VenueDetailPage';
import BookingPage from './pages/guest/BookingPage';
import OrderPage from './pages/guest/OrderPage';
import ProfilePage from './pages/guest/ProfilePage';
import FavoritesPage from './pages/guest/FavoritesPage';
import LoyaltyPage from './pages/guest/LoyaltyPage';
import PaymentsPage from './pages/guest/PaymentsPage';
import PreferencesPage from './pages/guest/PreferencesPage';
import BookingHistoryPage from './pages/guest/BookingHistoryPage';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';

// Business pages
import BusinessDashboard from './pages/business/DashboardPage';
import InventoryPage from './pages/business/InventoryPage';
import BookingsPage from './pages/business/BookingsPage';
import OrdersPage from './pages/business/OrdersPage';
import AnalyticsPage from './pages/business/AnalyticsPage';
import PricingPage from './pages/business/PricingPage';
import FeedbackPage from './pages/business/FeedbackPage';
import TasksPage from './pages/business/TasksPage';
import CampaignsPage from './pages/business/CampaignsPage';

// Admin pages
import AdminDashboard from './pages/admin/DashboardPage';
import AdminAnalyticsPage from './pages/admin/AnalyticsPage';
import UsersPage from './pages/admin/UsersPage';
import BusinessesPage from './pages/admin/BusinessesPage';

import ProtectedRoute from './components/ProtectedRoute';
import RoleProtectedRoute from './components/RoleProtectedRoute';

function App() {
  return (
    <Routes>
      {/* Public Auth Routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Guest Routes */}
      <Route element={<RootLayout><GuestLayout /></RootLayout>}>
        <Route path="/" element={<HomePage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/venues/:id" element={<VenueDetailPage />} />
        <Route
          path="/bookings/:venueId"
          element={
            <ProtectedRoute>
              <BookingPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/orders/:venueId"
          element={
            <ProtectedRoute>
              <OrderPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/favorites"
          element={
            <ProtectedRoute>
              <FavoritesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/loyalty"
          element={
            <ProtectedRoute>
              <LoyaltyPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/payments"
          element={
            <ProtectedRoute>
              <PaymentsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/preferences"
          element={
            <ProtectedRoute>
              <PreferencesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/bookings"
          element={
            <ProtectedRoute>
              <BookingHistoryPage />
            </ProtectedRoute>
          }
        />
      </Route>

      {/* Business Routes */}
      <Route
        element={
          <RootLayout>
            <RoleProtectedRoute allowedRoles={['business', 'admin']}>
              <BusinessLayout />
            </RoleProtectedRoute>
          </RootLayout>
        }
      >
        <Route path="/business" element={<BusinessDashboard />} />
        <Route path="/business/inventory" element={<InventoryPage />} />
        <Route path="/business/bookings" element={<BookingsPage />} />
        <Route path="/business/orders" element={<OrdersPage />} />
        <Route path="/business/analytics" element={<AnalyticsPage />} />
        <Route path="/business/pricing" element={<PricingPage />} />
        <Route path="/business/feedback" element={<FeedbackPage />} />
        <Route path="/business/tasks" element={<TasksPage />} />
        <Route path="/business/campaigns" element={<CampaignsPage />} />
      </Route>

      {/* Admin Routes */}
      <Route
        element={
          <RootLayout>
            <RoleProtectedRoute allowedRoles={['admin']}>
              <AdminLayout />
            </RoleProtectedRoute>
          </RootLayout>
        }
      >
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/admin/analytics" element={<AdminAnalyticsPage />} />
        <Route path="/admin/users" element={<UsersPage />} />
        <Route path="/admin/businesses" element={<BusinessesPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;

