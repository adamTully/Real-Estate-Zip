import React from "react";
import { MapPin, TrendingUp, Users, Target, Lightbulb, BarChart3, Home, Clock, DollarSign } from "lucide-react";
import MarkdownRenderer from "./MarkdownRenderer";

// Reusable UI components
const Card = ({ className = "", children, ...props }) => (
  <div className={`rounded-2xl shadow-sm border border-neutral-200 bg-white ${className}`} {...props}>
    {children}
  </div>
);

const Section = ({ title, icon: Icon, children, className = "" }) => (
  <div className={`space-y-4 ${className}`}>
    <div className="flex items-center gap-3 pb-2 border-b border-neutral-100">
      {Icon && <Icon className="w-5 h-5 text-neutral-600" />}
      <h2 className="text-xl font-semibold text-neutral-900">{title}</h2>
    </div>
    {children}
  </div>
);

const ContentBlock = ({ children, className = "" }) => (
  <div className={`bg-white rounded-xl p-6 border border-neutral-200 shadow-sm ${className}`}>
    {children}
  </div>
);

const MetricCard = ({ icon: Icon, label, value, change, color = "blue" }) => {
  const colors = {
    blue: "bg-blue-50 text-blue-600",
    green: "bg-green-50 text-green-600", 
    red: "bg-red-50 text-red-600",
    purple: "bg-purple-50 text-purple-600"
  };
  
  return (
    <Card className="p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${colors[color]}`}>
            <Icon className="w-5 h-5" />
          </div>
          <div>
            <p className="text-sm text-neutral-600">{label}</p>
            <p className="text-lg font-bold text-neutral-900">{value}</p>
          </div>
        </div>
        {change && (
          <div className={`text-sm font-medium ${
            change.startsWith('+') || change.startsWith('↑') 
              ? 'text-green-600' 
              : change.startsWith('-') || change.startsWith('↓')
              ? 'text-red-600'
              : 'text-neutral-600'
          }`}>
            {change}
          </div>
        )}
      </div>
    </Card>
  );
};

const MicroAreaCard = ({ area }) => (
  <Card className="p-5 hover:shadow-md transition-shadow">
    <div className="space-y-4">
      {/* Area Header */}
      <div>
        <h3 className="text-lg font-semibold text-neutral-900 mb-1">
          {area.name}
        </h3>
        <p className="text-sm text-neutral-600 flex items-center gap-1">
          <MapPin className="w-3 h-3" />
          {area.location_context}
        </p>
      </div>

      {/* Opportunity Driver */}
      <div className="bg-blue-50 p-3 rounded-lg border-l-4 border-l-blue-400">
        <p className="text-sm font-medium text-blue-900 mb-1">Why This Area Matters:</n>        
        <p className="text-blue-800 text-sm leading-relaxed">{area.opportunity_driver}</p>
      </div>

      {/* Likely Sellers */}
      <div>
        <p className="text-sm font-semibold text-neutral-700 mb-2">Likely Sellers:</p>
        <ul className="space-y-1">
          {area.likely_sellers.map((seller, idx) => (
            <li key={idx} className="text-sm text-neutral-600 flex items-start gap-2">
              <span className="w-1 h-1 bg-neutral-400 rounded-full mt-2 flex-shrink-0"></span>
              {seller}
            </li>
          ))}
        </ul>
      </div>

      {/* Pain Points */}
      <div>
        <p className="text-sm font-semibold text-neutral-700 mb-2">Key Pain Points:</p>
        <ul className="space-y-1">
          {area.pain_points.map((point, idx) => (
            <li key={idx} className="text-sm text-red-700 flex items-start gap-2">
              <span className="w-1 h-1 bg-red-500 rounded-full mt-2 flex-shrink-0"></span>
              {point}
            </li>
          ))}
        </ul>
      </div>

      {/* Prospecting Strategy */}
      <div className="bg-green-50 p-3 rounded-lg border-l-4 border-l-green-400">
        <p className="text-sm font-medium text-green-900 mb-1">Prospecting Strategy:</p>
        <p className="text-green-800 text-sm leading-relaxed">{area.prospecting_strategy}</p>
      </div>

      {/* Content Ideas */}
      <div>
        <p className="text-sm font-semibold text-neutral-700 mb-2">Content Ideas:</p>
        <div className="space-y-1">
          {area.content_ideas.map((idea, idx) => (
            <div key={idx} className="bg-purple-50 px-2 py-1 rounded text-xs text-purple-800">
              {idea}
            </div>
          ))}
        </div>
      </div>
    </div>
  </Card>
);

const SellerProfileCard = ({ profile }) => (
  <Card className="p-5">
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-neutral-900">
        {profile.profile}
      </h3>
      
      <p className="text-neutral-700 leading-relaxed">
        {profile.characteristics}
      </p>

      <div>
        <p className="text-sm font-semibold text-neutral-700 mb-2">Key Motivations:</p>
        <ul className="space-y-1">
          {profile.motivations.map((motivation, idx) => (
            <li key={idx} className="text-sm text-neutral-600 flex items-start gap-2">
              <span className="w-1 h-1 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
              {motivation}
            </li>
          ))}
        </ul>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-orange-50 p-3 rounded-lg">
          <p className="text-xs font-semibold text-orange-700 mb-1">Timing:</p>
          <p className="text-orange-800 text-sm">{profile.timing}</p>
        </div>
        
        <div className="bg-purple-50 p-3 rounded-lg">
          <p className="text-xs font-semibold text-purple-700 mb-1">Approach:</p>
          <p className="text-purple-800 text-sm">{profile.approach}</p>
        </div>
      </div>
    </div>
  </Card>
);

const TacticsList = ({ category, tactics }) => (
  <div className="bg-gradient-to-r from-neutral-50 to-blue-50 p-4 rounded-lg border-l-4 border-l-blue-400">
    <h4 className="font-semibold text-blue-900 mb-3">{category}</h4>
    <ul className="space-y-2">
      {tactics.map((tactic, idx) => (
        <li key={idx} className="text-blue-800 text-sm flex items-start gap-2">
          <Target className="w-3 h-3 mt-1 flex-shrink-0" />
          {tactic}
        </li>
      ))}
    </ul>
  </div>
);

const MarketResearchDetail = ({ data }) => {
  if (!data) return null;

  const hasNarrative = !!data.analysis_content;
  const narrative = data.analysis_content;

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatPercent = (value) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(1)}%`;
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-3">
        <h1 className="text-3xl font-bold text-neutral-900">
          Hidden Listing Opportunities
        </h1>
        <div className="flex items-center justify-center gap-2 text-neutral-600">
          <Home className="w-4 h-4" />
          <span className="text-lg">
            Market Research for {data.location?.city}, {data.location?.state}
          </span>
        </div>
        <p className="text-neutral-600 max-w-2xl mx-auto leading-relaxed">
          Comprehensive analysis of off-market opportunities, seller profiles, and prospecting strategies for your territory.
        </p>
      </div>

      {hasNarrative ? (
        <ContentBlock>
          <MarkdownRenderer content={narrative} className="prose-lg" />
        </ContentBlock>
      ) : (
        <>
          {/* Market Snapshot */}
          {data.market_snapshot && (
            <Section title="Market Snapshot" icon={BarChart3}>
              <div className="grid md:grid-cols-4 gap-4">
                <MetricCard
                  icon={DollarSign}
                  label="Median Price"
                  value={formatCurrency(data.market_snapshot.median_price)}
                  change={formatPercent(data.market_snapshot.yoy_change)}
                  color="green"
                />
                <MetricCard
                  icon={Clock}
                  label="Days on Market"
                  value={`${data.market_snapshot.dom_current} days`}
                  change={`vs ${data.market_snapshot.dom_last_year} last year`}
                  color="blue"
                />
                <MetricCard
                  icon={Home}
                  label="Months Inventory"
                  value={`${data.market_snapshot.months_inventory.toFixed(1)} months`}
                  color="purple"
                />
                <MetricCard
                  icon={TrendingUp}
                  label="Mortgage Rate"
                  value={`${data.market_snapshot.mortgage_rate.toFixed(2)}%`}
                  color="red"
                />
              </div>

              {data.market_context && (
                <ContentBlock className="bg-gradient-to-r from-neutral-50 to-orange-50 border-orange-200">
                  <div className="flex items-start gap-3">
                    <Lightbulb className="w-5 h-5 text-orange-600 mt-1 flex-shrink-0" />
                    <div>
                      <h3 className="text-lg font-semibold text-neutral-900 mb-2">Market Context</h3>
                      <p className="text-neutral-700 leading-relaxed">{data.market_context}</p>
                    </div>
                  </div>
                </ContentBlock>
              )}
            </Section>
          )}

          {/* Micro-Areas Analysis */}
          {data.micro_areas && (
            <Section title="High-Opportunity Micro-Areas" icon={MapPin}>
              <ContentBlock>
                <p className="text-neutral-700 mb-6 leading-relaxed">
                  Geographic areas with potential seller activity that other agents may be overlooking. 
                  Focus your prospecting efforts on these specific corridors and neighborhoods.
                </p>
              </ContentBlock>

              <div className="grid md:grid-cols-2 gap-6">
                {data.micro_areas.map((area, index) => (
                  <MicroAreaCard key={index} area={area} />
                ))}
              </div>
            </Section>
          )}

          {/* Seller Profiles */}
          {data.seller_profiles && (
            <Section title="Seller Profiles Most Likely to List" icon={Users}>
              <ContentBlock>
                <p className="text-neutral-700 mb-6 leading-relaxed">
                  Target seller segments based on current market conditions, lifecycle timing, and motivational factors. 
                  Tailor your approach and messaging to each profile's specific needs.
                </p>
              </ContentBlock>

              <div className="grid md:grid-cols-2 gap-6">
                {data.seller_profiles.map((profile, index) => (
                  <SellerProfileCard key={index} profile={profile} />
                ))}
              </div>
            </Section>
          )}

          {/* Actionable Takeaways */}
          {data.actionable_takeaways && (
            <Section title="Actionable Takeaways" icon={Target}>
              <ContentBlock>
                <p className="text-neutral-700 mb-6 leading-relaxed">
                  Specific tactics you can implement immediately for prospecting, content creation, and local marketing. 
                  Organized by channel for easy implementation and tracking.
                </p>
              </ContentBlock>

              <div className="grid md:grid-cols-2 gap-4">
                {data.actionable_takeaways.map((category, index) => (
                  <TacticsList
                    key={index}
                    category={category.category}
                    tactics={category.tactics}
                  />
                ))}
              </div>
            </Section>
          )}

          {/* Implementation Guide */}
          <ContentBlock className="bg-gradient-to-r from-neutral-50 to-green-50 border-green-200">
            <div className="flex items-start gap-3">
              <Lightbulb className="w-5 h-5 text-green-600 mt-1 flex-shrink-0" />
              <div>
                <h3 className="text-lg font-semibold text-neutral-900 mb-3">Next Steps</h3>
                <p className="text-neutral-700 leading-relaxed mb-4">
                  {data.next_steps}
                </p>
                <div className="space-y-2 text-sm text-green-800">
                  <div className="flex items-center gap-2">
                    <Target className="w-4 h-4" />
                    <span>Start with one micro-area for focused testing and optimization</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Target className="w-4 h-4" />
                    <span>Develop seller consultation packages for each profile type</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Target className="w-4 h-4" />
                    <span>Track response rates and adjust messaging based on results</span>
                  </div>
                </div>
              </div>
            </div>
          </ContentBlock>
        </>
      )}
    </div>
  );
};

export default MarketResearchDetail;