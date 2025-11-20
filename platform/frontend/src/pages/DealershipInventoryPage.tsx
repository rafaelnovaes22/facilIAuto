import React, { useState, useEffect } from 'react'
import {
    Box,
    Container,
    Heading,
    Text,
    VStack,
    Tabs,
    TabList,
    TabPanels,
    Tab,
    TabPanel,
    useToast,
    Select,
    HStack,
} from '@chakra-ui/react'
import { PhotoUpload } from '../components/admin/PhotoUpload'
import { PhotoGalleryManager } from '../components/admin/PhotoGalleryManager'
import { getCars, getCar } from '../services/api'
import { Car } from '../types'

const DealershipInventoryPage: React.FC = () => {
    const [selectedCarId, setSelectedCarId] = useState<string>('')
    const [cars, setCars] = useState<Car[]>([])
    const [currentCar, setCurrentCar] = useState<Car | null>(null)
    const toast = useToast()

    // Mock dealership ID for now (RobustCar)
    const DEALERSHIP_ID = 'robustcar'

    useEffect(() => {
        loadCars()
    }, [])

    useEffect(() => {
        if (selectedCarId) {
            loadCarDetails(selectedCarId)
        } else {
            setCurrentCar(null)
        }
    }, [selectedCarId])

    const loadCars = async () => {
        try {
            // Fetch cars for this dealership
            // Note: In a real app, we would filter by dealership_id in the API
            // For now, we fetch all and filter client-side or just take the first few
            const allCars = await getCars()
            const dealershipCars = allCars.filter(c => c.dealership_id === DEALERSHIP_ID)
            setCars(dealershipCars)

            if (dealershipCars.length > 0) {
                setSelectedCarId(dealershipCars[0].id)
            }
        } catch (error) {
            console.error('Error loading cars:', error)
            toast({
                title: 'Erro ao carregar veículos',
                status: 'error',
            })
        }
    }

    const loadCarDetails = async (id: string) => {
        try {
            const car = await getCar(id)
            setCurrentCar(car)
        } catch (error) {
            console.error('Error loading car details:', error)
        }
    }

    const handleUploadComplete = (url: string) => {
        toast({
            title: 'Foto enviada com sucesso!',
            status: 'success',
        })
        // Reload car details to show new photo
        if (selectedCarId) {
            loadCarDetails(selectedCarId)
        }
    }

    return (
        <Container maxW="container.xl" py={8}>
            <Heading mb={6}>Gestão de Estoque - Fotos</Heading>

            <Box bg="white" p={6} borderRadius="lg" shadow="sm" mb={6}>
                <VStack align="stretch" spacing={4}>
                    <Text fontWeight="bold">Selecione um Veículo:</Text>
                    <Select
                        value={selectedCarId}
                        onChange={(e) => setSelectedCarId(e.target.value)}
                        placeholder="Selecione um carro..."
                    >
                        {cars.map(car => (
                            <option key={car.id} value={car.id}>
                                {car.nome} ({car.ano}) - {car.cor}
                            </option>
                        ))}
                    </Select>
                </VStack>
            </Box>

            {currentCar && (
                <Box bg="white" p={6} borderRadius="lg" shadow="sm">
                    <HStack justify="space-between" mb={6}>
                        <Heading size="md">{currentCar.nome}</Heading>
                        <Text color="gray.500">ID: {currentCar.id}</Text>
                    </HStack>

                    <Tabs colorScheme="brand">
                        <TabList>
                            <Tab>Galeria Atual</Tab>
                            <Tab>Upload de Fotos</Tab>
                        </TabList>

                        <TabPanels>
                            <TabPanel>
                                <PhotoGalleryManager
                                    photos={currentCar.imagens || []}
                                />
                            </TabPanel>
                            <TabPanel>
                                <PhotoUpload
                                    dealershipId={DEALERSHIP_ID}
                                    carId={currentCar.id}
                                    onUploadComplete={handleUploadComplete}
                                />
                            </TabPanel>
                        </TabPanels>
                    </Tabs>
                </Box>
            )}
        </Container>
    )
}

export default DealershipInventoryPage
