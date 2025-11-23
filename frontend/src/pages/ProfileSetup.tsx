import {
  Box,
  Button,
  Input,
  FormControl,
  FormLabel,
  Heading,
  Textarea,
  VStack,
  useToast,
  Spinner,
  Select,
  useColorModeValue,
  Container,
  SimpleGrid,
  InputGroup,
  InputLeftElement,
  Icon,
  Text,
  Flex,
  Divider,
  HStack
} from "@chakra-ui/react";
import { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from 'react-router-dom';
import { 
  FaUser, FaEnvelope, FaPhone, FaLinkedin, FaGithub, 
  FaCloudUploadAlt, FaBriefcase, FaSave, FaMagic 
} from "react-icons/fa";

const ProfileSetup = () => {
  // --- LOGIC START (UNCHANGED) ---
  const toast = useToast();
  const navigate = useNavigate();
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState<any>({
    name: "",
    email: "",
    phone: "",
    linkedin: "",
    github: "",
    skills: "",
    projects: "",
    experience: "",
    education: "",
    role: "",
  });

  const handleResumeUpload = async () => {
    if (!resumeFile) return;

    setLoading(true);
    const form = new FormData();
    form.append("resume", resumeFile);

    try {
      const token = localStorage.getItem("token");
      const res = await axios.post("http://localhost:5000/api/parse-resume", form, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const parsed = res.data.data || res.data; // Handle potential nesting

      setFormData((prev: any) => ({
        ...prev,
        name: parsed.name || "",
        email: parsed.email || "",
        phone: parsed.phone || "",
        linkedin: parsed.linkedin || "",
        github: parsed.github || "",
        skills: Array.isArray(parsed.skills) ? parsed.skills.join(", ") : (parsed.skills || ""),
        projects: Array.isArray(parsed.projects) ? parsed.projects.map((p: any) => p.title || p).join(", ") : (parsed.projects || ""),
        experience: Array.isArray(parsed.experience) ? parsed.experience.map((e: any) => e.title || e).join(", ") : (parsed.experience || ""),
        education: Array.isArray(parsed.education) ? parsed.education.map((e: any) => e.degree || e).join(", ") : (parsed.education || ""),
      }));

      toast({ title: "Resume parsed successfully!", status: "success" });
    } catch (err) {
      toast({ title: "Failed to parse resume", status: "error" });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev: any) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await axios.post("http://localhost:5000/api/profile-setup", formData, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      toast({ title: "Profile setup complete!", status: "success" });
      navigate("/dashboard");
    } catch (err) {
      toast({ title: "Failed to submit profile", status: "error" });
    }
  };

  useEffect(() => {
    const fetchProfile = async () => {
      const token = localStorage.getItem("token");
      if (!token) return;
      try {
        const res = await axios.get("http://localhost:5000/api/profile", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setFormData((prev: any) => ({
          ...prev,
          ...res.data,
        }));
      } catch (err) {
        console.log("Profile not found or error occurred");
      }
    };

    fetchProfile();
  }, []);
  // --- LOGIC END ---

  // --- UI STYLES ---
  const bg = useColorModeValue("gray.50", "gray.900");
  const cardBg = useColorModeValue("white", "gray.800");
  const borderColor = useColorModeValue("gray.200", "gray.700");
  const uploadBg = useColorModeValue("teal.50", "whiteAlpha.100");
  const uploadBorder = useColorModeValue("teal.200", "teal.500");

  return (
    <Box minH="100vh" bg={bg} py={10}>
      <Container maxW="container.lg">
        
        {/* Header Section */}
        <VStack spacing={2} mb={8} textAlign="center">
          <Heading size="xl" color="teal.500">Your Candidate Profile</Heading>
          <Text color="gray.500">
            Keep your profile updated to get the most accurate AI interviews.
          </Text>
        </VStack>

        <SimpleGrid columns={{ base: 1, lg: 3 }} spacing={8} alignItems="start">
          
          {/* Left Column: Resume Upload & Actions */}
          <VStack spacing={6} as="aside">
            <Box 
              p={6} 
              bg={cardBg} 
              borderRadius="xl" 
              boxShadow="lg" 
              w="full" 
              border="1px solid" 
              borderColor={borderColor}
            >
              <VStack spacing={4}>
                <Box 
                  p={3} 
                  borderRadius="full" 
                  bg="teal.100" 
                  color="teal.600"
                >
                  <Icon as={FaCloudUploadAlt} boxSize={6} />
                </Box>
                <Heading size="sm" textAlign="center">Auto-Fill with Resume</Heading>
                <Text fontSize="xs" color="gray.500" textAlign="center">
                   Upload your PDF resume and let our AI extract your details automatically.
                </Text>

                <Box
                  w="full"
                  position="relative"
                  p={4}
                  border="2px dashed"
                  borderColor={uploadBorder}
                  borderRadius="lg"
                  bg={uploadBg}
                  transition="all 0.2s"
                  _hover={{ bg: "teal.100" }}
                >
                  <Input 
                    type="file" 
                    accept="application/pdf" 
                    height="100%"
                    width="100%"
                    position="absolute"
                    top="0"
                    left="0"
                    opacity="0"
                    cursor="pointer"
                    onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                  />
                  <VStack spacing={1}>
                    <Text fontWeight="bold" fontSize="sm" color="teal.600">
                      {resumeFile ? resumeFile.name : "Click to Upload PDF"}
                    </Text>
                  </VStack>
                </Box>

                <Button 
                  leftIcon={loading ? <Spinner size="sm"/> : <FaMagic />} 
                  colorScheme="teal" 
                  w="full" 
                  onClick={handleResumeUpload}
                  isDisabled={!resumeFile || loading}
                  isLoading={loading}
                  loadingText="Parsing..."
                >
                  Parse Resume
                </Button>
              </VStack>
            </Box>

            {/* Quick Tips Box */}
            <Box p={5} bg="blue.50" borderRadius="xl" borderLeft="4px solid" borderColor="blue.400" w="full">
               <Heading size="xs" color="blue.700" mb={2}>Tip:</Heading>
               <Text fontSize="sm" color="blue.600">
                 Adding detailed skills and project descriptions helps the AI ask deeper technical questions.
               </Text>
            </Box>
          </VStack>

          {/* Right Column: Form Fields */}
          <Box 
            gridColumn={{ lg: "span 2" }} 
            bg={cardBg} 
            p={8} 
            borderRadius="xl" 
            boxShadow="xl" 
            border="1px solid" 
            borderColor={borderColor}
          >
            {loading ? (
              <Flex direction="column" align="center" justify="center" minH="400px">
                <Spinner size="xl" color="teal.500" thickness="4px" />
                <Text mt={4} color="gray.500" fontWeight="medium">Extracting data from your resume...</Text>
              </Flex>
            ) : (
              <VStack spacing={6} align="stretch">
                
                {/* Section 1: Personal Info */}
                <Box>
                  <Heading size="sm" mb={4} color="gray.600" display="flex" alignItems="center">
                    <Icon as={FaUser} mr={2} color="teal.400" /> Personal Details
                  </Heading>
                  <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                    <FormControl>
                      <FormLabel fontSize="sm" fontWeight="bold">Full Name</FormLabel>
                      <Input name="name" value={formData.name} onChange={handleInputChange} placeholder="John Doe" focusBorderColor="teal.400" />
                    </FormControl>
                    
                    <FormControl>
                       <FormLabel fontSize="sm" fontWeight="bold">Target Role</FormLabel>
                       <Select name="role" value={formData.role} onChange={handleInputChange} placeholder="Select Role" focusBorderColor="teal.400">
                          <option value="sde">Software Development Engineer</option>
                          <option value="frontend">Frontend Developer</option>
                          <option value="backend">Backend Developer</option>
                          <option value="ds">Data Scientist</option>
                          <option value="sales">Sales Representative</option>
                       </Select>
                    </FormControl>

                    <FormControl>
                      <FormLabel fontSize="sm" fontWeight="bold">Email</FormLabel>
                      <InputGroup>
                        <InputLeftElement pointerEvents="none"><FaEnvelope color="gray.400"/></InputLeftElement>
                        <Input name="email" value={formData.email} onChange={handleInputChange} placeholder="you@example.com" />
                      </InputGroup>
                    </FormControl>

                    <FormControl>
                      <FormLabel fontSize="sm" fontWeight="bold">Phone</FormLabel>
                      <InputGroup>
                        <InputLeftElement pointerEvents="none"><FaPhone color="gray.400"/></InputLeftElement>
                        <Input name="phone" value={formData.phone} onChange={handleInputChange} placeholder="+1 234 567 890" />
                      </InputGroup>
                    </FormControl>
                  </SimpleGrid>
                </Box>
                
                <Divider />

                {/* Section 2: Professional Links */}
                <Box>
                   <Heading size="sm" mb={4} color="gray.600" display="flex" alignItems="center">
                    <Icon as={FaBriefcase} mr={2} color="teal.400" /> Professional Links
                  </Heading>
                  <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                    <FormControl>
                      <FormLabel fontSize="sm" fontWeight="bold">LinkedIn URL</FormLabel>
                      <InputGroup>
                        <InputLeftElement pointerEvents="none"><FaLinkedin color="#0077b5"/></InputLeftElement>
                        <Input name="linkedin" value={formData.linkedin} onChange={handleInputChange} placeholder="https://linkedin.com/in/..." />
                      </InputGroup>
                    </FormControl>

                    <FormControl>
                      <FormLabel fontSize="sm" fontWeight="bold">GitHub URL</FormLabel>
                      <InputGroup>
                        <InputLeftElement pointerEvents="none"><FaGithub color="#333"/></InputLeftElement>
                        <Input name="github" value={formData.github} onChange={handleInputChange} placeholder="https://github.com/..." />
                      </InputGroup>
                    </FormControl>
                  </SimpleGrid>
                </Box>

                <Divider />

                {/* Section 3: Detailed Info */}
                <Box>
                   <Heading size="sm" mb={4} color="gray.600" display="flex" alignItems="center">
                    <Icon as={FaMagic} mr={2} color="teal.400" /> Experience & Skills
                  </Heading>
                  <VStack spacing={4}>
                    <FormControl>
                      <FormLabel fontSize="sm" fontWeight="bold">Key Skills</FormLabel>
                      <Textarea name="skills" value={formData.skills} onChange={handleInputChange} placeholder="React, Python, Node.js..." rows={2} />
                    </FormControl>

                    <FormControl>
                      <FormLabel fontSize="sm" fontWeight="bold">Work Experience</FormLabel>
                      <Textarea name="experience" value={formData.experience} onChange={handleInputChange} placeholder="Software Engineer at X..." rows={3} />
                    </FormControl>

                    <FormControl>
                      <FormLabel fontSize="sm" fontWeight="bold">Projects</FormLabel>
                      <Textarea name="projects" value={formData.projects} onChange={handleInputChange} placeholder="E-commerce App, Portfolio..." rows={2} />
                    </FormControl>
                    
                    <FormControl>
                      <FormLabel fontSize="sm" fontWeight="bold">Education</FormLabel>
                      <Textarea name="education" value={formData.education} onChange={handleInputChange} placeholder="B.S. Computer Science..." rows={2} />
                    </FormControl>
                  </VStack>
                </Box>

                {/* Save Button */}
                <Box pt={4}>
                  <Button 
                    rightIcon={<FaSave />} 
                    colorScheme="teal" 
                    size="lg" 
                    w="full" 
                    onClick={handleSubmit}
                    boxShadow="lg"
                    _hover={{ transform: "translateY(-2px)", boxShadow: "xl" }}
                  >
                    Save Profile & Continue
                  </Button>
                </Box>

              </VStack>
            )}
          </Box>
        </SimpleGrid>
      </Container>
    </Box>
  );
};

export default ProfileSetup;