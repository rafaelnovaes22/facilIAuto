// 🎨 UX Especialist: Theme customizado Chakra UI
// Design tokens para sistema multi-tenant mobile-first

import { extendTheme, type ThemeConfig } from '@chakra-ui/react'

const config: ThemeConfig = {
  initialColorMode: 'light',
  useSystemColorMode: false,
}

const colors = {
  brand: {
    50: '#f0f8ff',
    100: '#e1f0fe',
    200: '#bae7ff',
    300: '#7dd3fc',
    400: '#38bdf8',
    500: '#0ea5e9', // Primary Blue - Technology/Structure
    600: '#0284c7',
    700: '#0369a1',
    800: '#075985',
    900: '#0c4a6e',
  },
  secondary: {
    50: '#f0fdf4',
    100: '#dcfce7',
    200: '#bbf7d0',
    300: '#86efac',
    400: '#4ade80',
    500: '#22c55e', // Action Green - Agility/Ecosystem/CTAs
    600: '#16a34a',
    700: '#15803d',
    800: '#166534',
    900: '#14532d',
  },
}

const fonts = {
  heading: `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`,
  body: `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`,
}

const styles = {
  global: {
    body: {
      bg: 'gray.50',
      color: 'gray.800',
    },
  },
}

const components = {
  Button: {
    baseStyle: {
      fontWeight: 'semibold',
      borderRadius: 'lg',
    },
    sizes: {
      lg: {
        h: '56px',
        fontSize: 'lg',
        px: '32px',
      },
    },
    variants: {
      solid: {
        bg: 'brand.500',
        color: 'white',
        _hover: {
          bg: 'brand.600',
          transform: 'translateY(-2px)',
          boxShadow: 'lg',
        },
        _active: {
          bg: 'brand.700',
          transform: 'translateY(0)',
        },
        transition: 'all 0.2s',
      },
      outline: {
        borderColor: 'brand.500',
        color: 'brand.500',
        _hover: {
          bg: 'brand.50',
        },
      },
    },
    defaultProps: {
      variant: 'solid',
      colorScheme: 'brand',
    },
  },
  Card: {
    baseStyle: {
      container: {
        borderRadius: 'xl',
        boxShadow: 'sm',
        _hover: {
          boxShadow: 'md',
          transform: 'translateY(-2px)',
        },
        transition: 'all 0.2s',
      },
    },
  },
  Input: {
    sizes: {
      lg: {
        field: {
          borderRadius: 'lg',
          h: '56px',
          fontSize: 'md',
        },
      },
    },
    variants: {
      filled: {
        field: {
          bg: 'white',
          borderWidth: '2px',
          borderColor: 'gray.200',
          _hover: {
            bg: 'white',
            borderColor: 'brand.300',
          },
          _focus: {
            bg: 'white',
            borderColor: 'brand.500',
            boxShadow: '0 0 0 1px var(--chakra-colors-brand-500)',
          },
        },
      },
    },
    defaultProps: {
      size: 'lg',
      variant: 'filled',
    },
  },
}

const theme = extendTheme({
  config,
  colors,
  fonts,
  styles,
  components,
})

export default theme

