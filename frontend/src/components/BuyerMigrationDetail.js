import React from "react";
import { MapPin, TrendingUp, Target, Lightbulb, Quote, AlertCircle } from "lucide-react";
import MarkdownRenderer from "./MarkdownRenderer";

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

function BuyerMigrationDetailView({ data }) {
  if (!data) return null;

  // Handle both real ChatGPT responses and structured data
  const content = data.analysis_content || data.market_overview || "No analysis available";
  const isRealData = !!data.analysis_content;

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-3">
        <h1 className="text-3xl font-bold text-neutral-900">
          Buyer Migration Intelligence
        </h1>
        <div className="flex items-center justify-center gap-2 text-neutral-600">
          <MapPin className="w-4 h-4" />
          <span className="text-lg">
            {data.location?.city}, {data.location?.state} Market Analysis
          </span>
        </div>
        <p className="text-neutral-600 max-w-2xl mx-auto leading-relaxed">
          {isRealData ? "Real-time market analysis powered by ChatGPT GPT-5" : "Analysis of buyer migration patterns and market opportunities for targeted marketing campaigns."}
        </p>
        {/* Build version badge for cache-busting visibility */}
        <div className="text-xs text-neutral-500">Build: bmd-v2</div>
        
        {/* Data Source Badge */}
        {isRealData && (
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
            <MapPin className="w-3 h-3" />
            Generated with {data.generated_with} • {data.timestamp ? new Date(data.timestamp).toLocaleDateString() : ""}
          </div>
        )}
      </div>

      {/* Real ChatGPT Content (Markdown) */}
      {isRealData ? (
        <ContentBlock>
          <MarkdownRenderer content={content} className="prose-lg" />
        </ContentBlock>
      ) : (
        /* Fallback structured content display */
        <>
          {/* Market Overview */}
          <Section title="Market Overview" icon={TrendingUp}>
            <ContentBlock>
              <p className="text-neutral-700 leading-relaxed text-lg">
                {data.market_overview}
              </p>
            </ContentBlock>
            
            {data.key_findings && (
              <div className="grid md:grid-cols-2 gap-4">
                {data.key_findings.map((finding, index) => (
                  <Highlight key={index} color={index === 0 ? "blue" : "green"}>
                    <h3 className="font-semibold mb-2">{finding.title}</h3>
                    <p className="text-sm leading-relaxed">{finding.content}</p>
                  </Highlight>
                ))}
              </div>
            )}
          </Section>

          {/* Why Buyers Are Moving */}
          {data.why_moving && (
            <Section title={`Why Buyers Are Moving to ${data.location?.city}`} icon={Target}>
              <div className="space-y-6">
                {data.why_moving.map((reason, index) => (
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

                    {reason.supporting_data && (
                      <div className="bg-neutral-50 p-3 rounded-lg">
                        <p className="text-sm text-neutral-600 leading-relaxed">
                          <strong>Key Insight:</strong> {reason.supporting_data}
                        </p>
                      </div>
                    )}
                  </ContentBlock>
                ))}
              </div>
            </Section>
          )}

          {/* Content Strategy Recommendations */}
          {data.content_strategy && (
            <Section title="Content Strategy to Attract These Buyers" icon={Lightbulb}>
              <div className="space-y-6">
                {data.content_strategy.map((strategy, index) => (
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
                      <p className="font-medium text-green-800">"{strategy.video_title}"</p>
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
          )}
        </>
      )}

      {/* Error Handling */}
      {data.error && (
        <ContentBlock className="bg-red-50 border-red-200">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 mt-1 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-semibold text-red-900 mb-2">Analysis Temporarily Unavailable</h3>
              <p className="text-red-800 leading-relaxed">
                We're experiencing temporary issues generating real-time analysis. Please try again in a few moments.
              </p>
              <p className="text-xs text-red-600 mt-2">Error: {data.error}</p>
            </div>
          </div>
        </ContentBlock>
      )}
    </div>
  );
}

export default BuyerMigrationDetailView;