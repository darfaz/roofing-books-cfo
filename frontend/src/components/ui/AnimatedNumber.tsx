import { motion, useSpring, useTransform } from 'framer-motion'
import { useEffect } from 'react'

interface AnimatedNumberProps {
  value: number
  format?: (value: number) => string
  className?: string
  duration?: number
}

export function AnimatedNumber({
  value,
  format = (v) => v.toLocaleString(),
  className = '',
  duration = 1,
}: AnimatedNumberProps) {
  const spring = useSpring(0, { duration: duration * 1000 })
  const display = useTransform(spring, (v) => format(Math.round(v)))

  useEffect(() => {
    spring.set(value)
  }, [spring, value])

  return <motion.span className={className}>{display}</motion.span>
}

interface AnimatedCurrencyProps {
  value: number
  className?: string
  duration?: number
  showSign?: boolean
}

export function AnimatedCurrency({
  value,
  className = '',
  duration = 1,
  showSign = false,
}: AnimatedCurrencyProps) {
  const format = (v: number) => {
    const formatted = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(Math.abs(v))

    if (showSign && v > 0) return `+${formatted}`
    if (v < 0) return `-${formatted.replace('-', '')}`
    return formatted
  }

  return <AnimatedNumber value={value} format={format} className={className} duration={duration} />
}

interface AnimatedPercentageProps {
  value: number
  className?: string
  duration?: number
  decimals?: number
}

export function AnimatedPercentage({
  value,
  className = '',
  duration = 1,
  decimals = 0,
}: AnimatedPercentageProps) {
  const format = (v: number) => `${v.toFixed(decimals)}%`
  return <AnimatedNumber value={value} format={format} className={className} duration={duration} />
}
