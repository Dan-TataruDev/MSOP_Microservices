import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { Search, User, LogOut, Menu, X, Heart, Trophy, Building2, LayoutDashboard } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/Button';

export default function GuestLayout() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isAdmin = user?.roles?.includes('admin');
  const isBusiness = user?.roles?.includes('business') || user?.roles?.includes('business_admin');
  const canAccessBusiness = isAdmin || isBusiness; // Admin can access business panel too

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen">
      <nav className="bg-white/80 backdrop-blur-md border-b border-slate-200/80 sticky top-0 z-50 shadow-sm">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">H</span>
              </div>
              <span className="text-xl font-bold gradient-text hidden sm:block">Hospitality</span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-6">
              <Link
                to="/search"
                className="flex items-center space-x-1 text-slate-700 hover:text-blue-600 transition-colors"
              >
                <Search className="w-4 h-4" />
                <span>Search</span>
              </Link>
              {isAuthenticated ? (
                <>
                  <Link
                    to="/favorites"
                    className="flex items-center space-x-1 text-slate-700 hover:text-pink-600 transition-colors"
                  >
                    <Heart className="w-4 h-4" />
                    <span>Favorites</span>
                  </Link>
                  <Link
                    to="/loyalty"
                    className="flex items-center space-x-1 text-slate-700 hover:text-purple-600 transition-colors"
                  >
                    <Trophy className="w-4 h-4" />
                    <span>Rewards</span>
                  </Link>
                  <Link
                    to="/profile"
                    className="flex items-center space-x-1 text-slate-700 hover:text-blue-600 transition-colors"
                  >
                    <User className="w-4 h-4" />
                    <span>{user?.name}</span>
                  </Link>
                  {canAccessBusiness && (
                    <Link
                      to="/business"
                      className="flex items-center space-x-1 text-slate-700 hover:text-emerald-600 transition-colors"
                    >
                      <Building2 className="w-4 h-4" />
                      <span>Business</span>
                    </Link>
                  )}
                  {isAdmin && (
                    <Link
                      to="/admin"
                      className="flex items-center space-x-1 text-slate-700 hover:text-orange-600 transition-colors"
                    >
                      <LayoutDashboard className="w-4 h-4" />
                      <span>Admin</span>
                    </Link>
                  )}
                  <Button variant="ghost" size="sm" onClick={handleLogout}>
                    <LogOut className="w-4 h-4 mr-2" />
                    Logout
                  </Button>
                </>
              ) : (
                <>
                  <Link to="/login">
                    <Button variant="ghost" size="sm">Login</Button>
                  </Link>
                  <Link to="/register">
                    <Button size="sm">Sign Up</Button>
                  </Link>
                </>
              )}
            </div>

            {/* Mobile Menu Button */}
            <button
              className="md:hidden p-2"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-slate-200">
              <div className="flex flex-col space-y-3">
                <Link
                  to="/search"
                  className="flex items-center space-x-2 text-slate-700 hover:text-blue-600"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <Search className="w-4 h-4" />
                  <span>Search</span>
                </Link>
                {isAuthenticated ? (
                  <>
                    <Link
                      to="/favorites"
                      className="flex items-center space-x-2 text-slate-700 hover:text-pink-600"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      <Heart className="w-4 h-4" />
                      <span>Favorites</span>
                    </Link>
                    <Link
                      to="/loyalty"
                      className="flex items-center space-x-2 text-slate-700 hover:text-purple-600"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      <Trophy className="w-4 h-4" />
                      <span>Rewards</span>
                    </Link>
                    <Link
                      to="/profile"
                      className="flex items-center space-x-2 text-slate-700 hover:text-blue-600"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      <User className="w-4 h-4" />
                      <span>{user?.name}</span>
                    </Link>
                    {canAccessBusiness && (
                      <Link
                        to="/business"
                        className="flex items-center space-x-2 text-slate-700 hover:text-emerald-600"
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        <Building2 className="w-4 h-4" />
                        <span>Business Panel</span>
                      </Link>
                    )}
                    {isAdmin && (
                      <Link
                        to="/admin"
                        className="flex items-center space-x-2 text-slate-700 hover:text-orange-600"
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        <LayoutDashboard className="w-4 h-4" />
                        <span>Admin Panel</span>
                      </Link>
                    )}
                    <button
                      onClick={() => {
                        handleLogout();
                        setMobileMenuOpen(false);
                      }}
                      className="flex items-center space-x-2 text-slate-700 hover:text-red-600"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Logout</span>
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      to="/login"
                      className="text-slate-700 hover:text-blue-600"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      Login
                    </Link>
                    <Link
                      to="/register"
                      className="text-blue-600 font-semibold"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      Sign Up
                    </Link>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </nav>
      <main>
        <Outlet />
      </main>
    </div>
  );
}

