import {
  Box, Flex, Tabs, TabList, TabPanels, Tab, TabPanel,
  SimpleGrid, Heading, Text, Button, Image,
  Collapse, useDisclosure, VStack, Spinner,
  Icon, HStack, Avatar, Badge, Spacer, Divider,
  useColorModeValue, Container
} from "@chakra-ui/react";
import { 
  FaHome, FaHistory, FaChartLine, FaChevronDown, 
  FaChevronUp, FaUserEdit, FaSignOutAlt, FaBriefcase 
} from "react-icons/fa";
import { useEffect, useState } from "react";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import axios from "axios";
import logoImage from '../assets/logo.png';
import HomeTab from "../components/HomeTab";
import PerformanceTab from "./PerformanceTab";

const Dashboard = () => {
  // --- STATE & LOGIC (UNCHANGED) ---
  const [interviews, setInterviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [tabIndex, setTabIndex] = useState(0);
  const { isOpen, onToggle } = useDisclosure();
  const navigate = useNavigate();

  // --- API CALLS (UNCHANGED) ---
  useEffect(() => {
    const fetchInterviews = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get("http://localhost:5000/api/interviews", {
          headers: { Authorization: `Bearer ${token}` },
        });
        // Handle both array and object responses
        const data = Array.isArray(res.data) ? res.data : res.data.interviews || [];
        setInterviews(data.reverse());
      } catch (err) {
        console.error("Failed to fetch interviews", err);
      } finally {
        setLoading(false);
      }
    };

    fetchInterviews();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  // --- UI COLORS ---
  const mainBg = useColorModeValue("gray.50", "gray.900");
  const cardBg = useColorModeValue("white", "gray.800");
  const sidebarBg = "#00203c";
  const activeTabBg = "teal.500";
  const hoverTabBg = "whiteAlpha.200";

  // --- LOADING STATE (UI ENHANCED) ---
  if (loading) return (
    <Box minH="100vh" display="flex" alignItems="center" justifyContent="center" bg={mainBg}>
      <VStack spacing={4}>
        <Spinner size="xl" color="teal.500" thickness="4px" speed="0.65s" emptyColor="gray.200" />
        <Text color="gray.500" fontWeight="medium">Loading your dashboard...</Text>
      </VStack>
    </Box>
  );

  return (
    <Flex height="100vh" overflow="hidden">
      
      {/* --- SIDEBAR --- */}
      <Box
        w={{ base: "60px", md: "260px" }}
        bg={sidebarBg}
        color="white"
        display="flex"
        flexDirection="column"
        boxShadow="4px 0 24px rgba(0,0,0,0.15)"
        zIndex={10}
        transition="width 0.2s"
      >
        {/* Logo Section */}
        <Box p={6} textAlign="center" borderBottom="1px solid rgba(255,255,255,0.1)">
           {logoImage ? (
              <Image src={logoImage} alt="AI Mock Interview" maxW="140px" mx="auto" display={{ base: "none", md: "block" }} />
           ) : (
              <Heading size="md" display={{ base: "none", md: "block" }}>InterviewAI</Heading>
           )}
           <Icon as={FaBriefcase} boxSize={6} display={{ base: "block", md: "none" }} mx="auto" />
        </Box>

        {/* Navigation Tabs */}
        <Tabs
          orientation="vertical"
          variant="unstyled"
          index={tabIndex}
          onChange={setTabIndex}
          display="flex"
          flexDirection="column"
          flex={1}
          pt={6}
        >
          <TabList w="100%" px={4} gap={2}>
            {/* Home Tab */}
            <Tab
              _selected={{ bg: activeTabBg, color: "white", boxShadow: "md" }}
              _hover={{ bg: hoverTabBg }}
              py={3} px={4}
              borderRadius="lg"
              justifyContent="flex-start"
              transition="all 0.2s"
              color="gray.300"
            >
              <HStack spacing={3}>
                <Icon as={FaHome} boxSize={5} />
                <Text display={{ base: "none", md: "block" }} fontWeight="medium">Dashboard</Text>
              </HStack>
            </Tab>

            {/* History Tab */}
            <Tab
              _selected={{ bg: activeTabBg, color: "white", boxShadow: "md" }}
              _hover={{ bg: hoverTabBg }}
              py={3} px={4}
              borderRadius="lg"
              justifyContent="flex-start"
              transition="all 0.2s"
              color="gray.300"
            >
              <HStack spacing={3}>
                <Icon as={FaHistory} boxSize={5} />
                <Text display={{ base: "none", md: "block" }} fontWeight="medium">History</Text>
              </HStack>
            </Tab>

            {/* Performance Tab */}
            <Tab
              _selected={{ bg: activeTabBg, color: "white", boxShadow: "md" }}
              _hover={{ bg: hoverTabBg }}
              py={3} px={4}
              borderRadius="lg"
              justifyContent="flex-start"
              transition="all 0.2s"
              color="gray.300"
            >
              <HStack spacing={3}>
                <Icon as={FaChartLine} boxSize={5} />
                <Text display={{ base: "none", md: "block" }} fontWeight="medium">Performance</Text>
              </HStack>
            </Tab>
          </TabList>
        </Tabs>

        {/* Settings / User Section */}
        <Box p={4} borderTop="1px solid rgba(255,255,255,0.1)">
          <Box 
            onClick={onToggle} 
            cursor="pointer" 
            p={3} 
            borderRadius="md" 
            _hover={{ bg: "whiteAlpha.200" }}
          >
            <Flex align="center" justify="space-between">
              <HStack>
                <Avatar size="sm" name="User" bg="teal.400" />
                <Box display={{ base: "none", md: "block" }} textAlign="left">
                  <Text fontSize="sm" fontWeight="bold">My Account</Text>
                  <Text fontSize="xs" opacity={0.7}>Settings</Text>
                </Box>
              </HStack>
              <Icon as={isOpen ? FaChevronUp : FaChevronDown} display={{ base: "none", md: "block" }} w={4} h={4} />
            </Flex>
          </Box>

          <Collapse in={isOpen} animateOpacity>
            <VStack align="stretch" spacing={1} mt={2} bg="blackAlpha.300" borderRadius="md" p={2}>
              <Button
                as={RouterLink}
                to="/profile-setup"
                leftIcon={<FaUserEdit />}
                size="sm"
                variant="ghost"
                justifyContent="flex-start"
                colorScheme="teal"
                _hover={{ bg: "whiteAlpha.200" }}
              >
                Edit Profile
              </Button>

              <Button
                onClick={handleLogout}
                leftIcon={<FaSignOutAlt />}
                size="sm"
                variant="ghost"
                justifyContent="flex-start"
                colorScheme="red"
                _hover={{ bg: "red.500", color: "white" }}
              >
                Logout
              </Button>
            </VStack>
          </Collapse>
        </Box>
      </Box>

      {/* --- MAIN CONTENT --- */}
      <Box flex="1" bg={mainBg} overflowY="auto" p={0}>
        <Container maxW="container.xl" py={8}>
          
          <Tabs index={tabIndex} onChange={setTabIndex} isManual variant="unstyled">
            <TabPanels>
              
              {/* --- HOME TAB --- */}
              <TabPanel p={0}>
                <Box bg={cardBg} borderRadius="xl" boxShadow="sm" p={1}>
                  <HomeTab />
                </Box>
              </TabPanel>

              {/* --- INTERVIEW HISTORY TAB --- */}
              <TabPanel p={0}>
                <Flex justify="space-between" align="center" mb={6}>
                  <Box>
                    <Heading size="lg" color="gray.700">Interview History</Heading>
                    <Text color="gray.500" mt={1}>Review your past sessions and feedback.</Text>
                  </Box>
                  {/* <Button as={RouterLink} to="/interview" colorScheme="teal" size="md" boxShadow="md">
                    + New Interview
                  </Button> */}
                </Flex>

                <Divider mb={6} />

                {interviews.length === 0 ? (
                   <Flex 
                      direction="column" 
                      align="center" 
                      justify="center" 
                      p={12} 
                      bg={cardBg} 
                      borderRadius="xl" 
                      boxShadow="sm"
                      border="2px dashed"
                      borderColor="gray.200"
                    >
                    <Icon as={FaHistory} boxSize={12} color="gray.300" mb={4} />
                    <Text fontSize="lg" color="gray.500">No interviews found yet.</Text>
                    <Button mt={4} colorScheme="teal" variant="outline" size="sm" as={RouterLink} to="/interview">
                      Start your first session
                    </Button>
                  </Flex>
                ) : (
                  <SimpleGrid columns={[1, null, 2, 3]} spacing={6}>
                    {interviews.map((item) => (
                      <RouterLink to={`/interview/${item._id}`} key={item._id} style={{ textDecoration: 'none' }}>
                        <Box
                          bg={cardBg}
                          borderRadius="xl"
                          boxShadow="sm"
                          p={6}
                          position="relative"
                          borderTop="4px solid"
                          borderColor={item.mode === 'full' ? 'purple.400' : 'teal.400'}
                          transition="all 0.2s"
                          _hover={{ transform: "translateY(-4px)", boxShadow: "xl" }}
                        >
                          <Flex justify="space-between" align="start" mb={3}>
                            <Badge 
                              colorScheme={item.mode === 'full' ? 'purple' : 'teal'} 
                              borderRadius="full" 
                              px={2}
                              textTransform="capitalize"
                            >
                              {item.mode}
                            </Badge>
                            <Text fontSize="xs" color="gray.400" fontWeight="bold">
                               {new Date(item.date).toLocaleDateString()}
                            </Text>
                          </Flex>

                          <Heading size="md" color="gray.700" mb={2} noOfLines={1} textTransform="capitalize">
                            {item.role || "Mock Interview"}
                          </Heading>

                          <Text fontSize="sm" color="gray.500" mb={5} noOfLines={2}>
                            {item.mode === 'full' 
                                ? "Technical, Coding & HR Rounds" 
                                : `Single ${item.mode} round session`}
                          </Text>

                          <Divider mb={4} />

                          <Flex justify="space-between" align="center">
                             <Text fontSize="xs" fontWeight="bold" color="gray.400">
                               VIEW FEEDBACK
                             </Text>
                             <Icon as={FaChevronDown} transform="rotate(-90deg)" color="gray.400" />
                          </Flex>
                        </Box>
                      </RouterLink>
                    ))}
                  </SimpleGrid>
                )}
              </TabPanel>

              {/* --- PERFORMANCE TAB --- */}
              <TabPanel p={0}>
                <Box bg={cardBg} borderRadius="xl" boxShadow="sm" p={6}>
                   <PerformanceTab interviewData={interviews} />
                </Box>
              </TabPanel>

            </TabPanels>
          </Tabs>
        </Container>
      </Box>
    </Flex>
  );
};

export default Dashboard;