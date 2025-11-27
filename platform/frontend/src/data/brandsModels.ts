// Lista estática de marcas e modelos populares no Brasil
// Organizado por popularidade das marcas e modelos em ordem alfabética

export const BRANDS_MODELS: Record<string, string[]> = {
    // Top 10 Marcas Mais Vendidas no Brasil
    'Chevrolet': [
        'Agile',
        'Camaro',
        'Captiva',
        'Classic',
        'Cobalt',
        'Corsa',
        'Cruze',
        'Equinox',
        'Montana',
        'Onix',
        'Onix Plus',
        'Prisma',
        'S10',
        'Sonic',
        'Spin',
        'Tracker',
        'Trailblazer',
    ].sort(),

    'Volkswagen': [
        'Amarok',
        'Crossfox',
        'Fox',
        'Gol',
        'Golf',
        'Jetta',
        'Nivus',
        'Passat',
        'Polo',
        'Saveiro',
        'Spacefox',
        'T-Cross',
        'Tiguan',
        'Up',
        'Virtus',
        'Voyage',
    ].sort(),

    'Fiat': [
        'Argo',
        'Cronos',
        'Doblo',
        'Ducato',
        'Fastback',
        'Fiorino',
        'Linea',
        'Mobi',
        'Palio',
        'Pulse',
        'Punto',
        'Siena',
        'Strada',
        'Toro',
        'Uno',
    ].sort(),

    'Hyundai': [
        'Azera',
        'Creta',
        'Elantra',
        'HB20',
        'HB20S',
        'HB20X',
        'i30',
        'ix35',
        'Santa Fe',
        'Sonata',
        'Tucson',
        'Veloster',
    ].sort(),

    'Toyota': [
        'Corolla',
        'Corolla Cross',
        'Etios',
        'Fielder',
        'Hilux',
        'Prius',
        'RAV4',
        'SW4',
        'Yaris',
    ].sort(),

    'Jeep': [
        'Compass',
        'Commander',
        'Grand Cherokee',
        'Renegade',
        'Wrangler',
    ].sort(),

    'Renault': [
        'Captur',
        'Duster',
        'Fluence',
        'Kardian',
        'Kwid',
        'Logan',
        'Oroch',
        'Sandero',
        'Stepway',
    ].sort(),

    'Honda': [
        'City',
        'Civic',
        'CR-V',
        'Fit',
        'HR-V',
        'WR-V',
    ].sort(),

    'Nissan': [
        'Frontier',
        'Kicks',
        'Leaf',
        'March',
        'Sentra',
        'Versa',
    ].sort(),

    'Ford': [
        'EcoSport',
        'Edge',
        'Fiesta',
        'Focus',
        'Fusion',
        'Ka',
        'Ranger',
        'Territory',
    ].sort(),

    // Outras Marcas Populares
    'Citroën': [
        'Aircross',
        'C3',
        'C4 Cactus',
        'C4 Lounge',
    ].sort(),

    'Peugeot': [
        '2008',
        '208',
        '3008',
        '308',
        'Partner',
    ].sort(),

    'Mitsubishi': [
        'ASX',
        'Eclipse Cross',
        'L200',
        'Lancer',
        'Outlander',
        'Pajero',
    ].sort(),

    'Kia': [
        'Bongo',
        'Cadenza',
        'Carnival',
        'Cerato',
        'Optima',
        'Picanto',
        'Sorento',
        'Soul',
        'Sportage',
        'Stinger',
    ].sort(),

    'Audi': [
        'A3',
        'A4',
        'A5',
        'A6',
        'A7',
        'A8',
        'Q3',
        'Q5',
        'Q7',
        'Q8',
        'TT',
    ].sort(),

    'BMW': [
        '118i',
        '120i',
        '320i',
        '328i',
        '428i',
        '530i',
        'X1',
        'X3',
        'X4',
        'X5',
        'X6',
    ].sort(),

    'Mercedes-Benz': [
        'A 200',
        'C 180',
        'C 200',
        'C 250',
        'CLA 200',
        'CLA 250',
        'E 250',
        'GLA 200',
        'GLC 250',
        'GLE 400',
    ].sort(),

    'Caoa Chery': [
        'Arrizo 5',
        'Arrizo 6',
        'Tiggo 2',
        'Tiggo 3X',
        'Tiggo 5X',
        'Tiggo 7',
        'Tiggo 8',
    ].sort(),

    'JAC': [
        'E-J7',
        'iEV20',
        'iEV40',
        'T40',
        'T50',
        'T60',
        'T8',
    ].sort(),

    'Suzuki': [
        'Grand Vitara',
        'Jimny',
        'S-Cross',
        'Swift',
        'Vitara',
    ].sort(),

    'Land Rover': [
        'Discovery',
        'Discovery Sport',
        'Evoque',
        'Range Rover',
        'Range Rover Sport',
        'Range Rover Velar',
    ].sort(),

    'Volvo': [
        'S60',
        'S90',
        'V40',
        'V60',
        'XC40',
        'XC60',
        'XC90 ',
    ].sort(),

    'Porsche': [
        '718',
        '911',
        'Cayenne',
        'Macan',
        'Panamera',
        'Taycan',
    ].sort(),
}

// Função para obter marcas ordenadas por popularidade
export const getBrandsOrdered = (): string[] => {
    return Object.keys(BRANDS_MODELS)
}

// Função para obter modelos de uma marca específica (ordenados alfabeticamente)
export const getModelsByBrand = (brand: string): string[] => {
    return BRANDS_MODELS[brand] || []
}

// Função para buscar marcas e modelos (para compatibilidade com a API)
export const getBrandsModelsStatic = (): Record<string, string[]> => {
    return BRANDS_MODELS
}
