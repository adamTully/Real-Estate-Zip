import React from "react";
import { Theme, Heading, Text, Card, Flex, Box, Badge, Table, Separator } from "@radix-ui/themes";
import { TrendingUp, TrendingDown, Minus, Users, DollarSign, Clock } from "lucide-react";

const BuyerMigrationDetail = ({ data }) => {
  if (!data) return null;

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'Increasing':
        return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'Decreasing':
        return <TrendingDown className="w-4 h-4 text-red-600" />;
      default:
        return <Minus className="w-4 h-4 text-gray-600" />;
    }
  };

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'High':
        return 'red';
      case 'Medium':
        return 'orange';
      case 'Low':
        return 'blue';
      default:
        return 'gray';
    }
  };

  return (
    <Theme>
      <Box className="space-y-8">
        {/* Header Section */}
        <Box>
          <Heading size="8" className="mb-2">
            Buyer Migration Intelligence
          </Heading>
          <Text size="5" color="gray" className="mb-4">
            {data.location?.city}, {data.location?.state} • ZIP {data.location?.zip_code}
          </Text>
          <Text size="3" color="gray">
            Analysis of buyer migration patterns and market opportunities for targeted marketing campaigns.
          </Text>
        </Box>

        <Separator size="4" />

        {/* Key Metrics Overview */}
        <Box>
          <Heading size="5" className="mb-4">Market Overview</Heading>
          <Flex gap="4" className="grid grid-cols-1 md:grid-cols-3">
            <Card className="p-4">
              <Flex align="center" gap="3">
                <Box className="p-2 bg-blue-50 rounded-lg">
                  <Users className="w-5 h-5 text-blue-600" />
                </Box>
                <Box>
                  <Text size="2" color="gray" className="block">Inbound Buyers</Text>
                  <Text size="5" weight="bold">{data.key_metrics?.inbound_buyer_percentage}%</Text>
                </Box>
              </Flex>
            </Card>

            <Card className="p-4">
              <Flex align="center" gap="3">
                <Box className="p-2 bg-green-50 rounded-lg">
                  <DollarSign className="w-5 h-5 text-green-600" />
                </Box>
                <Box>
                  <Text size="2" color="gray" className="block">Avg. Budget</Text>
                  <Text size="5" weight="bold">
                    {formatCurrency(data.market_opportunity?.avg_budget_range?.min)} - {formatCurrency(data.market_opportunity?.avg_budget_range?.max)}
                  </Text>
                </Box>
              </Flex>
            </Card>

            <Card className="p-4">
              <Flex align="center" gap="3">
                <Box className="p-2 bg-purple-50 rounded-lg">
                  <Clock className="w-5 h-5 text-purple-600" />
                </Box>
                <Box>
                  <Text size="2" color="gray" className="block">Avg. Timeline</Text>
                  <Text size="5" weight="bold">{data.market_opportunity?.timeline_months} months</Text>
                </Box>
              </Flex>
            </Card>
          </Flex>
        </Box>

        {/* Primary Inbound Markets */}
        <Box>
          <Heading size="5" className="mb-4">Primary Source Markets</Heading>
          <Card className="p-0">
            <Table.Root>
              <Table.Header>
                <Table.Row>
                  <Table.ColumnHeaderCell>Market</Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>Share of Buyers</Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>Trend</Table.ColumnHeaderCell>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {data.primary_markets?.map((market, index) => (
                  <Table.Row key={index}>
                    <Table.RowHeaderCell>
                      <Text size="3" weight="medium">{market.market}</Text>
                    </Table.RowHeaderCell>
                    <Table.Cell>
                      <Flex align="center" gap="2">
                        <Text size="3" weight="bold">{market.percentage}%</Text>
                        <Text size="2" color="gray">of inbound buyers</Text>
                      </Flex>
                    </Table.Cell>
                    <Table.Cell>
                      <Flex align="center" gap="2">
                        {getTrendIcon(market.trend)}
                        <Text size="2" color="gray">{market.trend}</Text>
                      </Flex>
                    </Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table.Root>
          </Card>
        </Box>

        {/* Migration Drivers */}
        <Box>
          <Heading size="5" className="mb-4">Key Migration Drivers</Heading>
          <Box className="space-y-4">
            {data.migration_drivers?.map((driver, index) => (
              <Card key={index} className="p-4">
                <Flex justify="between" align="start" className="mb-2">
                  <Text size="3" weight="medium" className="flex-1">
                    {driver.factor}
                  </Text>
                  <Badge color={getImpactColor(driver.impact)} size="2">
                    {driver.impact} Impact
                  </Badge>
                </Flex>
                <Text size="2" color="gray">
                  {driver.description}
                </Text>
              </Card>
            ))}
          </Box>
        </Box>

        {/* Property Type Preferences */}
        <Box>
          <Heading size="5" className="mb-4">Property Type Preferences</Heading>
          <Card className="p-4">
            <Box className="space-y-3">
              {data.market_opportunity?.property_types?.map((type, index) => (
                <Flex key={index} justify="between" align="center">
                  <Text size="3">{type.type}</Text>
                  <Flex align="center" gap="2">
                    <Text size="3" weight="bold">{type.percentage}%</Text>
                    <Box className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <Box 
                        className="h-full bg-blue-500 rounded-full"
                        style={{ width: `${type.percentage}%` }}
                      />
                    </Box>
                  </Flex>
                </Flex>
              ))}
            </Box>
          </Card>
        </Box>

        {/* Seasonal Patterns */}
        <Box>
          <Heading size="5" className="mb-4">Seasonal Migration Patterns</Heading>
          <Flex gap="4" className="grid grid-cols-1 md:grid-cols-3">
            <Card className="p-4">
              <Text size="2" color="gray" className="block mb-1">Peak Season</Text>
              <Text size="4" weight="bold" color="green">
                {data.seasonal_patterns?.peak_season}
              </Text>
            </Card>
            
            <Card className="p-4">
              <Text size="2" color="gray" className="block mb-1">Secondary Peak</Text>
              <Text size="4" weight="bold" color="orange">
                {data.seasonal_patterns?.secondary_peak}
              </Text>
            </Card>
            
            <Card className="p-4">
              <Text size="2" color="gray" className="block mb-1">Slowest Period</Text>
              <Text size="4" weight="bold" color="gray">
                {data.seasonal_patterns?.slowest_period}
              </Text>
            </Card>
          </Flex>
        </Box>

        {/* Buyer Profile */}
        <Box>
          <Heading size="5" className="mb-4">Target Buyer Profile</Heading>
          <Card className="p-4">
            <Text size="3" className="leading-relaxed">
              {data.market_opportunity?.buyer_profile}
            </Text>
          </Card>
        </Box>
      </Box>
    </Theme>
  );
};

export default BuyerMigrationDetail;