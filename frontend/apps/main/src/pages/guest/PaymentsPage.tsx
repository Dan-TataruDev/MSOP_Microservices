import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { CreditCard, FileText, Receipt, Download, RefreshCw, DollarSign, Calendar, CheckCircle, XCircle, Clock } from 'lucide-react';
import { apiServices, useAuthStore } from '@/stores/authStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { formatCurrency, formatDate, formatDateTime } from '@hospitality-platform/utils';

type TabType = 'payments' | 'invoices' | 'billing';

const statusColors: Record<string, string> = {
  completed: 'bg-green-100 text-green-700',
  pending: 'bg-yellow-100 text-yellow-700',
  processing: 'bg-blue-100 text-blue-700',
  failed: 'bg-red-100 text-red-700',
  refunded: 'bg-purple-100 text-purple-700',
};

export default function PaymentsPage() {
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState<TabType>('payments');

  // Get payments
  const { data: payments, isLoading: paymentsLoading, refetch: refetchPayments } = useQuery({
    queryKey: ['guest-payments', user?.id],
    queryFn: async () => {
      if (!user?.id) return [];
      try {
        return await apiServices.payments.getGuestPayments(user.id);
      } catch {
        return [];
      }
    },
    enabled: !!user?.id && activeTab === 'payments',
  });

  // Get invoices
  const { data: invoices, isLoading: invoicesLoading, refetch: refetchInvoices } = useQuery({
    queryKey: ['guest-invoices', user?.id],
    queryFn: async () => {
      if (!user?.id) return [];
      try {
        return await apiServices.payments.getGuestInvoices(user.id);
      } catch {
        return [];
      }
    },
    enabled: !!user?.id && activeTab === 'invoices',
  });

  // Get billing records
  const { data: billingRecords, isLoading: billingLoading, refetch: refetchBilling } = useQuery({
    queryKey: ['guest-billing', user?.id],
    queryFn: async () => {
      if (!user?.id) return [];
      try {
        return await apiServices.payments.getBillingRecords(user.id);
      } catch {
        return [];
      }
    },
    enabled: !!user?.id && activeTab === 'billing',
  });

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'paid':
        return <CheckCircle className="w-4 h-4" />;
      case 'failed':
      case 'cancelled':
        return <XCircle className="w-4 h-4" />;
      case 'pending':
      case 'processing':
        return <Clock className="w-4 h-4" />;
      default:
        return null;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900 mb-2">Payments & Billing</h1>
        <p className="text-slate-600">View your payment history, invoices, and billing records</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-slate-200">
        {(['payments', 'invoices', 'billing'] as TabType[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-6 py-3 font-medium transition-colors border-b-2 ${
              activeTab === tab
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Payments Tab */}
      {activeTab === 'payments' && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center">
                <CreditCard className="w-5 h-5 mr-2" />
                Payment History
              </CardTitle>
              <Button variant="outline" size="sm" onClick={() => refetchPayments()} leftIcon={<RefreshCw className="w-4 h-4" />}>
                Refresh
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {paymentsLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              </div>
            ) : payments && payments.length > 0 ? (
              <div className="space-y-4">
                {payments.map((payment: any) => (
                  <div key={payment.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h4 className="font-semibold text-slate-900">Payment #{payment.id.slice(0, 8)}</h4>
                          <span className={`px-2 py-1 rounded text-xs font-medium flex items-center gap-1 ${statusColors[payment.status] || 'bg-slate-100 text-slate-700'}`}>
                            {getStatusIcon(payment.status)}
                            {payment.status}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-slate-600">Amount:</span>
                            <p className="font-semibold text-slate-900">{formatCurrency(payment.amount, payment.currency || 'USD')}</p>
                          </div>
                          <div>
                            <span className="text-slate-600">Date:</span>
                            <p className="text-slate-900">{formatDate(payment.created_at)}</p>
                          </div>
                          {payment.payment_method && (
                            <div>
                              <span className="text-slate-600">Method:</span>
                              <p className="text-slate-900 capitalize">{payment.payment_method}</p>
                            </div>
                          )}
                          {payment.booking_id && (
                            <div>
                              <span className="text-slate-600">Booking:</span>
                              <p className="text-slate-900 font-mono text-xs">{payment.booking_id.slice(0, 8)}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <CreditCard className="w-12 h-12 text-slate-200 mx-auto mb-3" />
                <p className="text-slate-500">No payments found</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Invoices Tab */}
      {activeTab === 'invoices' && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center">
                <FileText className="w-5 h-5 mr-2" />
                Invoices
              </CardTitle>
              <Button variant="outline" size="sm" onClick={() => refetchInvoices()} leftIcon={<RefreshCw className="w-4 h-4" />}>
                Refresh
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {invoicesLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              </div>
            ) : invoices && invoices.length > 0 ? (
              <div className="space-y-4">
                {invoices.map((invoice: any) => (
                  <div key={invoice.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h4 className="font-semibold text-slate-900">Invoice {invoice.invoice_number || invoice.id.slice(0, 8)}</h4>
                          <span className={`px-2 py-1 rounded text-xs font-medium flex items-center gap-1 ${statusColors[invoice.status] || 'bg-slate-100 text-slate-700'}`}>
                            {getStatusIcon(invoice.status)}
                            {invoice.status}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-3">
                          <div>
                            <span className="text-slate-600">Amount:</span>
                            <p className="font-semibold text-slate-900">{formatCurrency(invoice.amount, invoice.currency || 'USD')}</p>
                          </div>
                          <div>
                            <span className="text-slate-600">Issued:</span>
                            <p className="text-slate-900">{formatDate(invoice.issued_date)}</p>
                          </div>
                          {invoice.due_date && (
                            <div>
                              <span className="text-slate-600">Due:</span>
                              <p className="text-slate-900">{formatDate(invoice.due_date)}</p>
                            </div>
                          )}
                          {invoice.paid_date && (
                            <div>
                              <span className="text-slate-600">Paid:</span>
                              <p className="text-slate-900">{formatDate(invoice.paid_date)}</p>
                            </div>
                          )}
                        </div>
                        {invoice.items && invoice.items.length > 0 && (
                          <div className="mt-3 pt-3 border-t border-slate-200">
                            <p className="text-xs font-semibold text-slate-600 mb-2">Items:</p>
                            <div className="space-y-1">
                              {invoice.items.map((item: any, idx: number) => (
                                <div key={idx} className="flex justify-between text-sm">
                                  <span className="text-slate-700">{item.description}</span>
                                  <span className="font-semibold text-slate-900">{formatCurrency(item.total, invoice.currency || 'USD')}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      <Button variant="outline" size="sm" leftIcon={<Download className="w-4 h-4" />}>
                        Download
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <FileText className="w-12 h-12 text-slate-200 mx-auto mb-3" />
                <p className="text-slate-500">No invoices found</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Billing Records Tab */}
      {activeTab === 'billing' && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center">
                <Receipt className="w-5 h-5 mr-2" />
                Billing Records
              </CardTitle>
              <Button variant="outline" size="sm" onClick={() => refetchBilling()} leftIcon={<RefreshCw className="w-4 h-4" />}>
                Refresh
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {billingLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              </div>
            ) : billingRecords && billingRecords.length > 0 ? (
              <div className="space-y-4">
                {billingRecords.map((record: any) => (
                  <div key={record.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h4 className="font-semibold text-slate-900 capitalize">{record.billing_type || 'Billing Record'}</h4>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${statusColors[record.status] || 'bg-slate-100 text-slate-700'}`}>
                            {record.status}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-slate-600">Amount:</span>
                            <p className="font-semibold text-slate-900">{formatCurrency(record.amount, record.currency || 'USD')}</p>
                          </div>
                          <div>
                            <span className="text-slate-600">Date:</span>
                            <p className="text-slate-900">{formatDate(record.created_at)}</p>
                          </div>
                          {record.booking_id && (
                            <div>
                              <span className="text-slate-600">Booking:</span>
                              <p className="text-slate-900 font-mono text-xs">{record.booking_id.slice(0, 8)}</p>
                            </div>
                          )}
                        </div>
                        {record.description && (
                          <p className="text-sm text-slate-600 mt-2">{record.description}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Receipt className="w-12 h-12 text-slate-200 mx-auto mb-3" />
                <p className="text-slate-500">No billing records found</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
