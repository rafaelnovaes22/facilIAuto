/**
 * Gerador de placeholders SVG para imagens de carros
 */

export const generatePlaceholder = (
  width: number,
  height: number,
  text: string = 'Sem Imagem'
): string => {
  const svg = `
    <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#E2E8F0"/>
      <text
        x="50%"
        y="50%"
        text-anchor="middle"
        dominant-baseline="middle"
        font-family="Arial, sans-serif"
        font-size="16"
        fill="#718096"
      >${text}</text>
    </svg>
  `
  
  return `data:image/svg+xml;base64,${btoa(svg)}`
}

export const CAR_PLACEHOLDER = generatePlaceholder(400, 300, 'Sem Imagem')
export const CAR_PLACEHOLDER_LARGE = generatePlaceholder(800, 600, 'Sem Imagem')
export const CAR_PLACEHOLDER_THUMB = generatePlaceholder(100, 75, '...')
export const CAR_PLACEHOLDER_LOADING = generatePlaceholder(400, 300, 'Carregando...')
export const CAR_PLACEHOLDER_LOADING_LARGE = generatePlaceholder(800, 600, 'Carregando...')

