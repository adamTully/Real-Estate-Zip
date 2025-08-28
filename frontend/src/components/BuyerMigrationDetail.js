import React from "react";
import { MapPin, TrendingUp, Target, Lightbulb, Quote } from "lucide-react";

// Typography-focused components
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

const Highlight = ({ children, color = "blue" }) => {
  const colors = {
    blue: "bg-blue-50 border-l-4 border-l-blue-400 text-blue-900",
    green: "bg-green-50 border-l-4 border-l-green-400 text-green-900", 
    orange: "bg-orange-50 border-l-4 border-l-orange-400 text-orange-900",
    purple: "bg-purple-50 border-l-4 border-l-purple-400 text-purple-900"
  };
  
  return (
    <div className={`p-4 rounded-r-lg ${colors[color]}`}>
      {children}
    </div>
  );
};

const BuyerMigrationDetail = ({ data }) => {
  if (!data) return null;

  // Parse the content - this would come from your prompt response
  const sampleContent = {
    overview: "Buyers relocating to Smyrna often come from high-cost metros where taxes and living expenses are high. Recent Redfin search data (May–Jul 2025) show that only 2% of people searching Smyrna homes were from outside the region; among those, the largest number came from New York (≈1,730 net inbound searches), followed by Los Angeles, Washington DC, San Francisco, Chicago, Miami, Cleveland, Philadelphia, Seattle and San Diego.",
    
    keyFindings: [
      {
        title: "Primary Source Markets",
        content: "New York leads with ~1,730 net inbound searches, followed by Los Angeles, Washington DC, San Francisco, and Chicago. Locally, most movers come from nearby Atlanta counties—Fulton, DeKalb, Cherokee, Paulding and Gwinnett."
      },
      {
        title: "Migration Drivers",
        content: "Many current homeowners are staying put because of low mortgage rates, so movers tend to come from farther away and are motivated by affordability and quality of life."
      }
    ],
    
    whyMoving: [
      {
        title: "Lower cost of living and housing",
        description: "Housing, utilities, groceries and transportation costs in Georgia are below the national average. A 2025 study found Georgia's cost of living to be ~$70,557 annually—the 12th-most affordable state—and housing costs are 21–22% lower than the national average.",
        highlight: "Average home prices in Smyrna ($480k median in July 2025) are far below those of NYC, Los Angeles or San Francisco."
      },
      {
        title: "Tax savings", 
        description: "Georgia's flat income tax rate is 5.39% for 2024 and is scheduled to decrease to 4.99% by 2029, and the average property-tax rate is ~0.72%. New York, by contrast, has nine income-tax brackets up to 10.9% and a statewide property-tax rate averaging 1.54%.",
        highlight: "Median real-estate taxes are about $2,048 in Georgia versus $6,303 in New York—buyers can save thousands per year."
      },
      {
        title: "More home for the money / lifestyle",
        description: "National Association of REALTORS® research shows that the biggest reasons people moved in 2024 were to be closer to family (30%) and to get more house for their money (21%); many also cited favorable taxes and safer areas.",
        highlight: "Smyrna offers walkable neighborhoods, the Silver Comet Trail, good restaurants, and proximity to Truist Park (home of the Atlanta Braves)."
      },
      {
        title: "Economic opportunity and climate",
        description: "Georgia's economy is strong, with major industries in manufacturing, real estate, professional services and healthcare. The Atlanta area hosts Fortune 500 companies such as Delta Air Lines, The Home Depot and Coca-Cola.",
        highlight: "Warm weather and access to outdoor recreation attract remote workers and retirees who want mild winters."
      }
    ],
    
    contentStrategy: [
      {
        focus: "Cost-of-living and tax comparisons",
        hook: "Escape high taxes—discover how moving from New York to Smyrna can save you 30% or more on taxes and living costs.",
        keywords: ["cost of living Smyrna vs. NY/LA/Chicago", "Georgia property tax savings", "affordable homes Smyrna"],
        videoTitle: "Why New Yorkers Are Flocking to Smyrna, GA: Huge Tax & Housing Savings Explained",
        strategy: "Use charts comparing median home prices and tax rates. Highlight that buyers can afford larger homes while lowering their tax burden."
      },
      {
        focus: "Lifestyle and community features",
        hook: "From walking trails to Truist Park—see why Smyrna offers the perfect work-life balance.",
        keywords: ["Smyrna lifestyle", "family-friendly neighborhoods", "outdoor activities", "schools"],
        videoTitle: "Living in Smyrna, GA: Top Amenities, Schools and Things to Do (2025 Update)",
        strategy: "Provide tours of local attractions, discuss school options and spotlight community events. Show what everyday life looks like."
      },
      {
        focus: "Relocation stories targeting specific metros",
        hook: "Moving from Los Angeles to Smyrna? Here's what you need to know about housing, taxes and jobs.",
        keywords: ["moving from LA to Atlanta/Smyrna", "relocate from Chicago to Smyrna", "Atlanta job market"],
        videoTitle: "Leaving LA: How Smyrna, GA Offers Affordable Luxury and a Growing Job Market",
        strategy: "Use case studies or interviews with clients who relocated. Discuss common pain points and how Smyrna addressed them."
      }
    ]
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-3">
        <h1 className="text-3xl font-bold text-neutral-900">
          Buyer Migration Intelligence
        </h1>
        <div className="flex items-center justify-center gap-2 text-neutral-600">
          <MapPin className="w-4 h-4" />
          <span className="text-lg">Smyrna, Georgia Market Analysis</span>
        </div>
        <p className="text-neutral-600 max-w-2xl mx-auto leading-relaxed">
          Analysis of buyer migration patterns and market opportunities for targeted marketing campaigns.
        </p>
      </div>

      {/* Market Overview */}
      <Section title="Market Overview" icon={TrendingUp}>
        <ContentBlock>
          <p className="text-neutral-700 leading-relaxed text-lg">
            {sampleContent.overview}
          </p>
        </ContentBlock>
        
        <div className="grid md:grid-cols-2 gap-4">
          {sampleContent.keyFindings.map((finding, index) => (
            <Highlight key={index} color={index === 0 ? "blue" : "green"}>
              <h3 className="font-semibold mb-2">{finding.title}</h3>
              <p className="text-sm leading-relaxed">{finding.content}</p>
            </Highlight>
          ))}
        </div>
      </Section>

      {/* Why Buyers Are Moving */}
      <Section title="Why Buyers Are Moving to Smyrna" icon={Target}>
        <div className="space-y-6">
          {sampleContent.whyMoving.map((reason, index) => (
            <ContentBlock key={index} className="space-y-4">
              <h3 className="text-lg font-semibold text-neutral-900 flex items-center gap-2">
                <span className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold">
                  {index + 1}
                </span>
                {reason.title}
              </h3>
              
              <p className="text-neutral-700 leading-relaxed">
                {reason.description}
              </p>
              
              <Highlight color="orange">
                <div className="flex items-start gap-2">
                  <Quote className="w-4 h-4 mt-1 flex-shrink-0" />
                  <p className="text-sm font-medium leading-relaxed">
                    {reason.highlight}
                  </p>
                </div>
              </Highlight>
            </ContentBlock>
          ))}
        </div>
      </Section>

      {/* Content Strategy Recommendations */}
      <Section title="Content Strategy to Attract These Buyers" icon={Lightbulb}>
        <div className="space-y-6">
          {sampleContent.contentStrategy.map((strategy, index) => (
            <ContentBlock key={index} className="space-y-4">
              <h3 className="text-lg font-semibold text-neutral-900">
                {index + 1}. {strategy.focus}
              </h3>
              
              {/* Hook */}
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg border-l-4 border-l-blue-400">
                <p className="font-medium text-neutral-800">
                  <span className="text-blue-600 font-semibold">Hook: </span>
                  "{strategy.hook}"
                </p>
              </div>

              {/* Keywords */}
              <div>
                <p className="text-sm font-semibold text-neutral-600 mb-2">Target Keywords:</p>
                <div className="flex flex-wrap gap-2">
                  {strategy.keywords.map((keyword, idx) => (
                    <span key={idx} className="px-3 py-1 bg-neutral-100 text-neutral-700 text-sm rounded-full">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>

              {/* Video Title */}
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <p className="text-sm font-semibold text-green-700 mb-1">Suggested Video Title:</p>
                <p className="font-medium text-green-800">"{strategy.videoTitle}"</p>
              </div>

              {/* Strategy */}
              <div className="bg-neutral-50 p-4 rounded-lg">
                <p className="text-sm font-semibold text-neutral-600 mb-2">Implementation Strategy:</p>
                <p className="text-neutral-700 leading-relaxed">{strategy.strategy}</p>
              </div>
            </ContentBlock>
          ))}
        </div>
      </Section>

      {/* Next Steps */}
      <ContentBlock className="bg-gradient-to-r from-neutral-50 to-blue-50 border-blue-200">
        <h3 className="text-lg font-semibold text-neutral-900 mb-3">Next Steps</h3>
        <p className="text-neutral-700 leading-relaxed">
          By creating data-driven, metro-specific content that compares costs, taxes and lifestyle, you'll attract buyers from the cities most interested in Smyrna. Use SEO-friendly keywords, social-media hooks and video formats to meet them where they search—YouTube, Instagram, TikTok and Google.
        </p>
      </ContentBlock>
    </div>
  );
};

export default BuyerMigrationDetail;