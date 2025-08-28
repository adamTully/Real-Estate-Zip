import React from "react";
import { TrendingUp, TrendingDown, Minus, Users, DollarSign, Clock } from "lucide-react";

// Simple components without Radix themes for now
const Card = ({ className = "", children, ...props }) => (
  <div className={`rounded-2xl shadow-lg border border-neutral-200 bg-white p-6 ${className}`} {...props}>
    {children}
  </div>
);

const Badge = ({ children, color = "gray" }) => {
  const colors = {
    red: "bg-red-100 text-red-800",
    orange: "bg-orange-100 text-orange-800", 
    blue: "bg-blue-100 text-blue-800",
    gray: "bg-gray-100 text-gray-800"
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[color]}`}>
      {children}
    </span>
  );
};

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
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header Section */}
      <div>
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Buyer Migration Intelligence
        </h1>
        <p className="text-xl text-gray-600 mb-4">
          {data.location?.city}, {data.location?.state} • ZIP {data.location?.zip_code}
        </p>
        <p className="text-gray-600">
          Analysis of buyer migration patterns and market opportunities for targeted marketing campaigns.
        </p>
      </div>

      <hr className="border-gray-200" />

      {/* Key Metrics Overview */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Market Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-50 rounded-xl">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Inbound Buyers</p>
                <p className="text-2xl font-bold text-gray-900">{data.key_metrics?.inbound_buyer_percentage}%</p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-50 rounded-xl">
                <DollarSign className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Avg. Budget Range</p>
                <p className="text-lg font-bold text-gray-900">
                  {formatCurrency(data.market_opportunity?.avg_budget_range?.min)} - {formatCurrency(data.market_opportunity?.avg_budget_range?.max)}
                </p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-50 rounded-xl">
                <Clock className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Avg. Timeline</p>
                <p className="text-2xl font-bold text-gray-900">{data.market_opportunity?.timeline_months} months</p>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Primary Inbound Markets */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Primary Source Markets</h2>
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Market</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Share of Buyers</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Trend</th>
                </tr>
              </thead>
              <tbody>
                {data.primary_markets?.map((market, index) => (
                  <tr key={index} className="border-b border-gray-100">
                    <td className="py-4 px-4">
                      <span className="font-medium text-gray-900">{market.market}</span>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-2">
                        <span className="text-lg font-bold text-gray-900">{market.percentage}%</span>
                        <span className="text-sm text-gray-600">of inbound buyers</span>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-2">
                        {getTrendIcon(market.trend)}
                        <span className="text-sm text-gray-600">{market.trend}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      {/* Migration Drivers */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Key Migration Drivers</h2>
        <div className="space-y-4">
          {data.migration_drivers?.map((driver, index) => (
            <Card key={index}>
              <div className="flex justify-between items-start mb-3">
                <h3 className="text-lg font-medium text-gray-900 flex-1">
                  {driver.factor}
                </h3>
                <Badge color={getImpactColor(driver.impact)}>
                  {driver.impact} Impact
                </Badge>
              </div>
              <p className="text-gray-600">
                {driver.description}
              </p>
            </Card>
          ))}
        </div>
      </div>

      {/* Property Type Preferences */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Property Type Preferences</h2>
        <Card>
          <div className="space-y-4">
            {data.market_opportunity?.property_types?.map((type, index) => (
              <div key={index} className="flex justify-between items-center">
                <span className="text-gray-900 font-medium">{type.type}</span>
                <div className="flex items-center gap-3">
                  <span className="text-lg font-bold text-gray-900">{type.percentage}%</span>
                  <div className="w-24 h-3 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-500 rounded-full transition-all duration-500"
                      style={{ width: `${type.percentage}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Seasonal Patterns */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Seasonal Migration Patterns</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="text-center">
            <p className="text-sm text-gray-600 mb-2">Peak Season</p>
            <p className="text-xl font-bold text-green-600">
              {data.seasonal_patterns?.peak_season}
            </p>
          </Card>
          
          <Card className="text-center">
            <p className="text-sm text-gray-600 mb-2">Secondary Peak</p>
            <p className="text-xl font-bold text-orange-600">
              {data.seasonal_patterns?.secondary_peak}
            </p>
          </Card>
          
          <Card className="text-center">
            <p className="text-sm text-gray-600 mb-2">Slowest Period</p>
            <p className="text-xl font-bold text-gray-600">
              {data.seasonal_patterns?.slowest_period}
            </p>
          </Card>
        </div>
      </div>

      {/* Buyer Profile */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Target Buyer Profile</h2>
        <Card>
          <p className="text-gray-700 leading-relaxed text-lg">
            {data.market_opportunity?.buyer_profile}
          </p>
        </Card>
      </div>
    </div>
  );
};

export default BuyerMigrationDetail;