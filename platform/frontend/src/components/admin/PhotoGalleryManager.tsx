import React from 'react'
import {
    Box,
    Image,
    SimpleGrid,
    IconButton,
    Text,
    useToast,
    Badge,
} from '@chakra-ui/react'
import { FaTrash, FaStar } from 'react-icons/fa'

interface PhotoGalleryManagerProps {
    photos: string[]
    onDeletePhoto?: (photoUrl: string) => void
    onSetMainPhoto?: (photoUrl: string) => void
}

export const PhotoGalleryManager: React.FC<PhotoGalleryManagerProps> = ({
    photos,
    onDeletePhoto,
    onSetMainPhoto,
}) => {
    const toast = useToast()

    const handleDelete = (photoUrl: string) => {
        // In a real app, we would call the API here
        if (onDeletePhoto) {
            onDeletePhoto(photoUrl)
        } else {
            toast({
                title: 'Funcionalidade em desenvolvimento',
                description: 'A exclusão de fotos será implementada em breve.',
                status: 'info',
            })
        }
    }

    if (!photos || photos.length === 0) {
        return (
            <Box p={5} textAlign="center" borderWidth="1px" borderRadius="md" borderStyle="dashed">
                <Text color="gray.500">Nenhuma foto cadastrada para este veículo.</Text>
            </Box>
        )
    }

    return (
        <SimpleGrid columns={{ base: 2, md: 3, lg: 4 }} spacing={4}>
            {photos.map((photo, index) => (
                <Box
                    key={index}
                    position="relative"
                    borderRadius="md"
                    overflow="hidden"
                    boxShadow="sm"
                    _hover={{ boxShadow: 'md' }}
                    role="group"
                >
                    <Image
                        src={photo}
                        alt={`Foto ${index + 1}`}
                        objectFit="cover"
                        w="100%"
                        h="150px"
                    />

                    {index === 0 && (
                        <Badge
                            position="absolute"
                            top={2}
                            left={2}
                            colorScheme="yellow"
                            variant="solid"
                            display="flex"
                            alignItems="center"
                        >
                            <FaStar style={{ marginRight: '4px' }} /> Principal
                        </Badge>
                    )}

                    <Box
                        position="absolute"
                        top={0}
                        left={0}
                        right={0}
                        bottom={0}
                        bg="blackAlpha.600"
                        opacity={0}
                        transition="opacity 0.2s"
                        _groupHover={{ opacity: 1 }}
                        display="flex"
                        alignItems="center"
                        justifyContent="center"
                        gap={2}
                    >
                        {index !== 0 && onSetMainPhoto && (
                            <IconButton
                                aria-label="Definir como principal"
                                icon={<FaStar />}
                                colorScheme="yellow"
                                size="sm"
                                onClick={() => onSetMainPhoto(photo)}
                            />
                        )}
                        <IconButton
                            aria-label="Excluir foto"
                            icon={<FaTrash />}
                            colorScheme="red"
                            size="sm"
                            onClick={() => handleDelete(photo)}
                        />
                    </Box>
                </Box>
            ))}
        </SimpleGrid>
    )
}
