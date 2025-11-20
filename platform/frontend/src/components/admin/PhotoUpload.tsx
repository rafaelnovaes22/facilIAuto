import React, { useState, useRef } from 'react'
import {
    Box,
    Button,
    Text,
    VStack,
    HStack,
    Icon,
    useToast,
    Progress,
    Image,
    SimpleGrid,
    IconButton,
} from '@chakra-ui/react'
import { FaCloudUploadAlt, FaTrash, FaCheckCircle } from 'react-icons/fa'
import { uploadCarImage } from '../../services/api'

interface PhotoUploadProps {
    dealershipId: string
    carId: string
    onUploadComplete?: (url: string) => void
}

interface UploadingFile {
    file: File
    preview: string
    progress: number
    status: 'pending' | 'uploading' | 'success' | 'error'
    error?: string
}

export const PhotoUpload: React.FC<PhotoUploadProps> = ({
    dealershipId,
    carId,
    onUploadComplete,
}) => {
    const [isDragging, setIsDragging] = useState(false)
    const [files, setFiles] = useState<UploadingFile[]>([])
    const fileInputRef = useRef<HTMLInputElement>(null)
    const toast = useToast()

    const handleDragEnter = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setIsDragging(true)
    }

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setIsDragging(false)
    }

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setIsDragging(false)

        const droppedFiles = Array.from(e.dataTransfer.files)
        handleFiles(droppedFiles)
    }

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            const selectedFiles = Array.from(e.target.files)
            handleFiles(selectedFiles)
        }
    }

    const handleFiles = (newFiles: File[]) => {
        // Filter images only
        const imageFiles = newFiles.filter(file => file.type.startsWith('image/'))

        if (imageFiles.length !== newFiles.length) {
            toast({
                title: 'Arquivos inválidos ignorados',
                description: 'Apenas imagens são permitidas.',
                status: 'warning',
                duration: 3000,
                isClosable: true,
            })
        }

        const newUploadingFiles: UploadingFile[] = imageFiles.map(file => ({
            file,
            preview: URL.createObjectURL(file),
            progress: 0,
            status: 'pending',
        }))

        setFiles(prev => [...prev, ...newUploadingFiles])
    }

    const uploadFiles = async () => {
        const pendingFiles = files.filter(f => f.status === 'pending')

        if (pendingFiles.length === 0) return

        for (let i = 0; i < files.length; i++) {
            if (files[i].status === 'pending') {
                // Update status to uploading
                setFiles(prev =>
                    prev.map((f, index) =>
                        index === i ? { ...f, status: 'uploading', progress: 10 } : f
                    )
                )

                try {
                    // Simulate progress
                    setFiles(prev =>
                        prev.map((f, index) =>
                            index === i ? { ...f, progress: 50 } : f
                        )
                    )

                    const result = await uploadCarImage(dealershipId, carId, files[i].file)

                    setFiles(prev =>
                        prev.map((f, index) =>
                            index === i ? { ...f, status: 'success', progress: 100 } : f
                        )
                    )

                    if (onUploadComplete) {
                        onUploadComplete(result.url)
                    }

                } catch (error) {
                    console.error('Upload error:', error)
                    setFiles(prev =>
                        prev.map((f, index) =>
                            index === i ? { ...f, status: 'error', error: 'Falha no upload' } : f
                        )
                    )
                    toast({
                        title: 'Erro no upload',
                        description: `Falha ao enviar ${files[i].file.name}`,
                        status: 'error',
                        duration: 3000,
                        isClosable: true,
                    })
                }
            }
        }
    }

    const removeFile = (index: number) => {
        setFiles(prev => prev.filter((_, i) => i !== index))
    }

    return (
        <VStack spacing={4} width="100%" align="stretch">
            <Box
                border="2px dashed"
                borderColor={isDragging ? 'brand.500' : 'gray.300'}
                bg={isDragging ? 'brand.50' : 'gray.50'}
                borderRadius="md"
                p={10}
                textAlign="center"
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                transition="all 0.2s"
                _hover={{ borderColor: 'brand.500', bg: 'gray.100' }}
                cursor="pointer"
                onClick={() => fileInputRef.current?.click()}
            >
                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileInput}
                    style={{ display: 'none' }}
                    multiple
                    accept="image/*"
                />
                <Icon as={FaCloudUploadAlt} w={10} h={10} color="gray.400" mb={3} />
                <Text fontWeight="bold" color="gray.600">
                    Arraste e solte fotos aqui
                </Text>
                <Text fontSize="sm" color="gray.500">
                    ou clique para selecionar arquivos
                </Text>
            </Box>

            {files.length > 0 && (
                <VStack align="stretch" spacing={3}>
                    <HStack justify="space-between">
                        <Text fontWeight="bold">Arquivos ({files.length})</Text>
                        <Button
                            size="sm"
                            colorScheme="brand"
                            onClick={uploadFiles}
                            isDisabled={!files.some(f => f.status === 'pending')}
                        >
                            Enviar Todas
                        </Button>
                    </HStack>

                    <SimpleGrid columns={{ base: 1, md: 2 }} spacing={3}>
                        {files.map((file, index) => (
                            <HStack
                                key={index}
                                p={2}
                                borderWidth="1px"
                                borderRadius="md"
                                bg="white"
                                spacing={3}
                            >
                                <Image
                                    src={file.preview}
                                    boxSize="50px"
                                    objectFit="cover"
                                    borderRadius="sm"
                                />
                                <VStack align="start" flex={1} spacing={0}>
                                    <Text fontSize="sm" noOfLines={1} fontWeight="medium">
                                        {file.file.name}
                                    </Text>
                                    <Text fontSize="xs" color="gray.500">
                                        {(file.file.size / 1024).toFixed(1)} KB
                                    </Text>
                                    {file.status === 'uploading' && (
                                        <Progress
                                            value={file.progress}
                                            size="xs"
                                            width="100%"
                                            colorScheme="brand"
                                            hasStripe
                                            isAnimated
                                        />
                                    )}
                                    {file.status === 'success' && (
                                        <Text fontSize="xs" color="green.500" display="flex" alignItems="center">
                                            <Icon as={FaCheckCircle} mr={1} /> Sucesso
                                        </Text>
                                    )}
                                    {file.status === 'error' && (
                                        <Text fontSize="xs" color="red.500">
                                            {file.error}
                                        </Text>
                                    )}
                                </VStack>
                                <IconButton
                                    aria-label="Remover"
                                    icon={<FaTrash />}
                                    size="sm"
                                    variant="ghost"
                                    colorScheme="red"
                                    onClick={(e) => {
                                        e.stopPropagation()
                                        removeFile(index)
                                    }}
                                    isDisabled={file.status === 'uploading'}
                                />
                            </HStack>
                        ))}
                    </SimpleGrid>
                </VStack>
            )}
        </VStack>
    )
}
