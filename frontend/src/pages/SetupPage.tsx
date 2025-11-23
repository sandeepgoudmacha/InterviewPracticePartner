import {
  Box, Button, Container, Heading, Select, Text, VStack,
  useToast, Spinner, useColorModeValue, Flex, Icon, SimpleGrid,
  FormControl, FormLabel, InputGroup, InputLeftElement, Badge
} from '@chakra-ui/react';
import { fetchWithAuth } from '../utils/fetchWithAuth';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaBriefcase, FaUserTie, FaLaptopCode, FaRocket, FaCheckCircle } from 'react-icons/fa';

export default function SetupPage() {
  // --- LOGIC START (UNCHANGED) ---
  const [role, setRole] = useState('')
  const [interviewType, setInterviewType] = useState<'full' | 'custom'>('full')
  const [customRound, setCustomRound] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const toast = useToast()
  const navigate = useNavigate()

  const handleStart = async () => {
    if (!role || (interviewType === 'custom' && !customRound)) {
      toast({
        title: 'Incomplete form',
        description: 'Please select all required fields.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      })
      return
    }

    setIsLoading(true)
    const formData = new FormData()
    formData.append("role", role)
    formData.append("interview_type", interviewType)
    formData.append("custom_round", customRound)

    try {
      const res = await fetchWithAuth("http://localhost:5000/api/setup", {
        method: "POST",
        body: formData,
      })

      if (res.ok) {
        navigate('/interview')
      } else {
        const err = await res.json()
        toast({ title: 'Setup failed', description: err.detail, status: 'error' })
      }
    } catch (err) {
      toast({ title: 'Setup error', description: 'Could not reach server.', status: 'error' })
    } finally {
      setIsLoading(false)
    }
  }
  // --- LOGIC END ---

  // --- UI STYLES ---
  const bg = useColorModeValue("gray.50", "gray.900")
  const cardBg = useColorModeValue("white", "gray.800")
  const borderColor = useColorModeValue("gray.200", "gray.700")
  const activeBorderColor = "teal.400"
  const activeBg = useColorModeValue("teal.50", "whiteAlpha.100")

  // Helper for Selection Cards
  const SelectionCard = ({ value, title, description, icon }: any) => {
    const isSelected = interviewType === value;
    return (
      <Box
        as="button"
        onClick={() => setInterviewType(value)}
        w="100%"
        p={4}
        border="2px solid"
        borderColor={isSelected ? activeBorderColor : borderColor}
        bg={isSelected ? activeBg : "transparent"}
        borderRadius="xl"
        textAlign="left"
        transition="all 0.2s"
        _hover={{ borderColor: "teal.300", transform: "translateY(-2px)", shadow: "md" }}
        position="relative"
      >
        <Flex align="center" mb={2}>
          <Icon as={icon} color={isSelected ? "teal.500" : "gray.400"} boxSize={5} mr={3} />
          <Text fontWeight="bold" color={isSelected ? "teal.600" : "gray.600"}>
            {title}
          </Text>
          {isSelected && <Icon as={FaCheckCircle} color="teal.500" ml="auto" />}
        </Flex>
        <Text fontSize="sm" color="gray.500" ml={8}>
          {description}
        </Text>
      </Box>
    );
  };

  return (
    <Flex minH="90vh" align="center" justify="center" bg={bg} p={4}>
      <Container maxW="lg">
        <Box
          p={8}
          borderRadius="2xl"
          boxShadow="2xl"
          bg={cardBg}
          border="1px solid"
          borderColor={borderColor}
        >
          <VStack spacing={6} align="stretch">
            
            {/* Header */}
            <Box textAlign="center" mb={2}>
              <Icon as={FaRocket} w={10} h={10} color="teal.400" mb={3} />
              <Heading size="lg" color="teal.500" letterSpacing="tight">
                New Session
              </Heading>
              <Text color="gray.500" mt={2} fontSize="sm">
                Configure your AI mock interview parameters below.
              </Text>
            </Box>

            {/* Role Selection */}
            <FormControl>
              <FormLabel fontWeight="bold" color="gray.600">Target Role</FormLabel>
              <InputGroup>
                <InputLeftElement pointerEvents="none" children={<FaBriefcase color="gray.400" />} />
                <Select
                  placeholder="Select your target role"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  pl={10}
                  height="50px"
                  borderRadius="lg"
                  focusBorderColor="teal.400"
                  icon={<FaBriefcase />} // Fallback if InputLeftElement overlaps oddly in some themes
                >
                  <option value="sde">Software Developer (SDE)</option>
                  <option value="DS">Data Scientist</option>
                  <option value="frontend">Frontend Developer</option>
                  <option value="backend">Backend Developer</option>
                  <option value="sales">Sales Representative</option>
                </Select>
              </InputGroup>
            </FormControl>

            {/* Interview Type Selection (Replaced Radio with Cards) */}
            <FormControl>
              <FormLabel fontWeight="bold" color="gray.600" mb={3}>Session Mode</FormLabel>
              <SimpleGrid columns={1} spacing={3}>
                <SelectionCard 
                  value="full" 
                  title="Full Interview" 
                  description="Complete simulation: Tech, Coding & HR rounds."
                  icon={FaLaptopCode}
                />
                <SelectionCard 
                  value="custom" 
                  title="Custom Round" 
                  description="Focus on a specific area (e.g. Behavioral only)."
                  icon={FaUserTie}
                />
              </SimpleGrid>
            </FormControl>

            {/* Conditional Custom Round Select */}
            {interviewType === 'custom' && (
              <Box 
                p={4} 
                bg={useColorModeValue("gray.50", "gray.700")} 
                borderRadius="lg" 
                borderLeft="4px solid" 
                borderColor="teal.400"
                animation="fadeIn 0.3s ease-in-out"
              >
                <FormControl>
                  <FormLabel fontWeight="bold" fontSize="sm" color="gray.600">
                    Select Specific Round
                  </FormLabel>
                  <Select
                    placeholder="Choose round type"
                    onChange={(e) => setCustomRound(e.target.value)}
                    bg={cardBg}
                    borderRadius="md"
                    size="sm"
                    focusBorderColor="teal.400"
                  >
                    {role === 'sales' ? (
                      <>
                        <option value="sales">Hiring Manager (Practical)</option>
                        <option value="behavioral">Senior Leadership (Fit)</option>
                      </>
                    ) : (
                      <>
                        <option value="technical">Technical Deep Dive</option>
                        <option value="behavioral">Behavioral (HR)</option>
                        
                      </>
                    )}
                  </Select>
                </FormControl>
              </Box>
            )}

            {/* Action Button */}
            <Button
              colorScheme="teal"
              size="lg"
              w="full"
              h="56px"
              fontSize="md"
              fontWeight="bold"
              borderRadius="xl"
              boxShadow="lg"
              _hover={{ transform: 'translateY(-2px)', boxShadow: 'xl' }}
              transition="all 0.2s"
              onClick={handleStart}
              isDisabled={isLoading}
              isLoading={isLoading}
              loadingText="Initializing AI..."
              leftIcon={!isLoading ? <FaRocket /> : undefined}
            >
              Start Interview
            </Button>

          </VStack>
        </Box>
      </Container>
    </Flex>
  );
}