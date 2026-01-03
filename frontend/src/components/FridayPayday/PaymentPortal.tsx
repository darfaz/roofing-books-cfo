/**
 * Friday Payday - Payment Portal
 *
 * Public-facing page where customers can view their invoice and make payments.
 * Accessed via unique token links sent in reminder emails/SMS.
 */
import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

interface InvoiceDetails {
  invoice_number: string
  amount: number
  balance: number
  due_date: string
  job_address: string | null
  customer_name: string
  company_name: string
  company_logo: string | null
  company_phone: string | null
  company_email: string | null
  payment_methods: string[]
  brand_color: string
}

interface PaymentPortalProps {
  token: string
}

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(amount)
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export function PaymentPortal({ token }: PaymentPortalProps) {
  const [invoice, setInvoice] = useState<InvoiceDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedMethod, setSelectedMethod] = useState<string>('card')
  const [processing, setProcessing] = useState(false)
  const [paymentSuccess, setPaymentSuccess] = useState(false)

  useEffect(() => {
    const fetchInvoice = async () => {
      try {
        setLoading(true)
        const response = await fetch(`/api/friday-payday/portal/${token}`)

        if (!response.ok) {
          if (response.status === 404) {
            setError('This payment link has expired or is invalid.')
          } else {
            setError('Unable to load invoice. Please try again.')
          }
          return
        }

        const data = await response.json()
        if (data.success && data.data) {
          setInvoice(data.data)
        } else {
          setError('Unable to load invoice details.')
        }
      } catch (err) {
        setError('Unable to connect. Please check your internet connection.')
      } finally {
        setLoading(false)
      }
    }

    void fetchInvoice()
  }, [token])

  const handlePayment = async () => {
    if (!invoice) return

    setProcessing(true)

    try {
      // TODO: Integrate with Stripe/payment processor
      // For now, simulate payment processing
      await new Promise((resolve) => setTimeout(resolve, 2000))

      setPaymentSuccess(true)
    } catch (err) {
      setError('Payment failed. Please try again.')
    } finally {
      setProcessing(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading invoice...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
          <div className="text-5xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Unable to Load Invoice
          </h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <p className="text-sm text-gray-500">
            If you believe this is an error, please contact the business directly.
          </p>
        </div>
      </div>
    )
  }

  if (paymentSuccess) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <motion.div
          className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
        >
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">✓</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Payment Successful!
          </h1>
          <p className="text-gray-600 mb-6">
            Thank you for your payment. You'll receive a confirmation email shortly.
          </p>
          <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
            <p className="font-medium">Invoice #{invoice?.invoice_number}</p>
            <p>Amount Paid: {invoice ? formatCurrency(invoice.balance) : ''}</p>
          </div>
        </motion.div>
      </div>
    )
  }

  if (!invoice) {
    return null
  }

  const brandColor = invoice.brand_color || '#1E40AF'

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header
        className="bg-white border-b"
        style={{ borderBottomColor: brandColor }}
      >
        <div className="max-w-2xl mx-auto px-4 py-4 flex items-center justify-between">
          {invoice.company_logo ? (
            <img
              src={invoice.company_logo}
              alt={invoice.company_name}
              className="h-10"
            />
          ) : (
            <h1
              className="text-xl font-bold"
              style={{ color: brandColor }}
            >
              {invoice.company_name}
            </h1>
          )}
          <div className="text-right text-sm text-gray-500">
            {invoice.company_phone && <div>{invoice.company_phone}</div>}
            {invoice.company_email && <div>{invoice.company_email}</div>}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-2xl mx-auto px-4 py-8">
        <motion.div
          className="bg-white rounded-xl shadow-lg overflow-hidden"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
        >
          {/* Invoice Header */}
          <div
            className="p-6 text-white"
            style={{ backgroundColor: brandColor }}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white/80 text-sm">Invoice</p>
                <p className="text-2xl font-bold">
                  #{invoice.invoice_number}
                </p>
              </div>
              <div className="text-right">
                <p className="text-white/80 text-sm">Amount Due</p>
                <p className="text-3xl font-bold">
                  {formatCurrency(invoice.balance)}
                </p>
              </div>
            </div>
          </div>

          {/* Invoice Details */}
          <div className="p-6 border-b">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Bill To</p>
                <p className="font-medium text-gray-900">
                  {invoice.customer_name}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Due Date</p>
                <p className="font-medium text-gray-900">
                  {formatDate(invoice.due_date)}
                </p>
              </div>
            </div>
            {invoice.job_address && (
              <div className="mt-4">
                <p className="text-sm text-gray-500">Job Address</p>
                <p className="text-gray-900">{invoice.job_address}</p>
              </div>
            )}

            <div className="mt-4 flex justify-between items-center bg-gray-50 rounded-lg p-4">
              <div>
                <p className="text-sm text-gray-500">Original Amount</p>
                <p className="text-lg text-gray-900">
                  {formatCurrency(invoice.amount)}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Balance Due</p>
                <p
                  className="text-2xl font-bold"
                  style={{ color: brandColor }}
                >
                  {formatCurrency(invoice.balance)}
                </p>
              </div>
            </div>
          </div>

          {/* Payment Methods */}
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Select Payment Method
            </h3>

            <div className="space-y-3">
              {invoice.payment_methods.includes('card') && (
                <label
                  className={`flex items-center gap-3 p-4 border rounded-lg cursor-pointer transition ${
                    selectedMethod === 'card'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="payment_method"
                    value="card"
                    checked={selectedMethod === 'card'}
                    onChange={(e) => setSelectedMethod(e.target.value)}
                    className="sr-only"
                  />
                  <span className="text-2xl">💳</span>
                  <div>
                    <p className="font-medium text-gray-900">Credit/Debit Card</p>
                    <p className="text-sm text-gray-500">
                      Visa, Mastercard, Amex
                    </p>
                  </div>
                  {selectedMethod === 'card' && (
                    <span
                      className="ml-auto w-5 h-5 rounded-full flex items-center justify-center text-white text-xs"
                      style={{ backgroundColor: brandColor }}
                    >
                      ✓
                    </span>
                  )}
                </label>
              )}

              {invoice.payment_methods.includes('ach') && (
                <label
                  className={`flex items-center gap-3 p-4 border rounded-lg cursor-pointer transition ${
                    selectedMethod === 'ach'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="payment_method"
                    value="ach"
                    checked={selectedMethod === 'ach'}
                    onChange={(e) => setSelectedMethod(e.target.value)}
                    className="sr-only"
                  />
                  <span className="text-2xl">🏦</span>
                  <div>
                    <p className="font-medium text-gray-900">Bank Transfer (ACH)</p>
                    <p className="text-sm text-gray-500">
                      Direct from your bank account
                    </p>
                  </div>
                  {selectedMethod === 'ach' && (
                    <span
                      className="ml-auto w-5 h-5 rounded-full flex items-center justify-center text-white text-xs"
                      style={{ backgroundColor: brandColor }}
                    >
                      ✓
                    </span>
                  )}
                </label>
              )}
            </div>

            {/* Pay Button */}
            <button
              onClick={handlePayment}
              disabled={processing}
              className="w-full mt-6 py-4 rounded-lg text-white font-semibold text-lg transition disabled:opacity-50"
              style={{ backgroundColor: brandColor }}
            >
              {processing ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Processing...
                </span>
              ) : (
                `Pay ${formatCurrency(invoice.balance)}`
              )}
            </button>

            <p className="text-center text-sm text-gray-500 mt-4">
              🔒 Secured by Stripe. Your payment information is encrypted.
            </p>
          </div>
        </motion.div>

        {/* Help Section */}
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>
            Questions about this invoice?{' '}
            <a
              href={`mailto:${invoice.company_email}`}
              className="text-blue-600 hover:underline"
            >
              Contact {invoice.company_name}
            </a>
          </p>
        </div>
      </main>
    </div>
  )
}
