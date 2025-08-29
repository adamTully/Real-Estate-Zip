import React from "react";
import { Search, Youtube, TrendingUp, Target, Lightbulb, MessageSquare, BarChart3 } from "lucide-react";
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

const KeywordCard = ({ keyword, context, searchBehavior }) => (
  <Card className="p-4 hover:shadow-md transition-shadow">
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Search className="w-4 h-4 text-blue-600" />
        <span className="font-medium text-lg text-neutral-900">"{keyword}"</span>
      </div>
      <p className="text-neutral-700 text-sm leading-relaxed">
        {context}
      </p>
      <div className="bg-blue-50 p-2 rounded-lg">
        <p className="text-blue-800 text-xs font-medium">
          <strong>Search Intent:</strong> {searchBehavior}
        </p>
      </div>
    </div>
  </Card>
);

const QuestionCard = ({ question, context, intent }) => (
  <Card className="p-4 hover:shadow-md transition-shadow">
    <div className="space-y-3">
      <div className="flex items-start gap-2">
        <MessageSquare className="w-4 h-4 text-green-600 mt-1 flex-shrink-0" />
        <h3 className="font-medium text-neutral-900 leading-tight">
          "{question}"
        </h3>
      </div>
      <p className="text-neutral-700 text-sm leading-relaxed ml-6">
        {context}
      </p>
      <div className="bg-green-50 p-2 rounded-lg ml-6">
        <p className="text-green-800 text-xs font-medium">
          <strong>User Intent:</strong> {intent}
        </p>
      </div>
    </div>
  </Card>
);

const VideoTitleCard = ({ title, strategy, targetKeywords, contentFocus }) => (
  <Card className="p-5 hover:shadow-md transition-shadow">
    <div className="space-y-4">
      <div className="flex items-start gap-3">
        <Youtube className="w-5 h-5 text-red-600 mt-1 flex-shrink-0" />
        <h3 className="font-medium text-lg text-neutral-900 leading-tight">
          "{title}"
        </h3>
      </div>
      
      <div className="bg-red-50 p-3 rounded-lg">
        <p className="text-sm text-red-800 leading-relaxed">
          <strong>Strategy:</strong> {strategy}
        </p>
      </div>

      <div className="space-y-2">
        <p className="text-xs font-semibold text-neutral-600">Target Keywords:</p>
        <div className="flex flex-wrap gap-1">
          {targetKeywords.map((keyword, idx) => (
            <span key={idx} className="px-2 py-1 bg-neutral-100 text-neutral-700 text-xs rounded-md">
              {keyword}
            </span>
          ))}
        </div>
      </div>

      <div className="bg-neutral-50 p-3 rounded-lg">
        <p className="text-xs text-neutral-700">
          <strong>Content Focus:</strong> {contentFocus}
        </p>
      </div>
    </div>
  </Card>
);

const StrategyInsight = ({ category, recommendation }) => (
  <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-4 rounded-lg border-l-4 border-l-purple-400">
    <h4 className="font-semibold text-purple-900 mb-2">{category}</h4>
    <p className="text-purple-800 text-sm leading-relaxed">{recommendation}</p>
  </div>
);

const SeoYouTubeDetail = ({ data }) => {
  if (!data) return null;

  const hasNarrative = !!data.analysis_content;
  const narrative = data.analysis_content;

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-3">
        <h1 className="text-3xl font-bold text-neutral-900">
          SEO & YouTube Trends Analysis
        </h1>
        <div className="flex items-center justify-center gap-2 text-neutral-600">
          <Search className="w-4 h-4" />
          <span className="text-lg">
            {data.location?.city}, {data.location?.state} Market Analysis
          </span>
        </div>
        <p className="text-neutral-600 max-w-2xl mx-auto leading-relaxed">
          Comprehensive keyword research and content strategy based on what buyers are actually searching for in your market.
        </p>
      </div>

      {hasNarrative ? (
        <ContentBlock>
          <MarkdownRenderer content={narrative} className="prose-lg" />
        </ContentBlock>
      ) : (
        <>
          {/* Optimization Summary */}
          {data.optimization_summary && (
            <ContentBlock className="bg-gradient-to-r from-neutral-50 to-blue-50 border-blue-200">
              <div className="flex items-start gap-3">
                <TrendingUp className="w-5 h-5 text-blue-600 mt-1 flex-shrink-0" />
                <div>
                  <h3 className="text-lg font-semibold text-neutral-900 mb-2">Market Search Insights</h3>
                  <p className="text-neutral-700 leading-relaxed">{data.optimization_summary}</p>
                </div>
              </div>
            </ContentBlock>
          )}

          {/* High-Volume Keywords */}
          {data.high_volume_keywords && (
            <Section title="High-Volume Local Keywords" icon={BarChart3}>
              <ContentBlock>
                <p className="text-neutral-700 mb-6 leading-relaxed">
                  These are common short phrases that capture broad interest and high search volume. 
                  Focus your primary content and landing pages around these terms.
                </p>
              </ContentBlock>
              
              <div className="grid md:grid-cols-2 gap-4">
                {data.high_volume_keywords.map((item, index) => (
                  <KeywordCard
                    key={index}
                    keyword={item.keyword}
                    context={item.context}
                    searchBehavior={item.search_behavior}
                  />
                ))}
              </div>
            </Section>
          )}

          {/* Long-Tail Questions */}
          {data.long_tail_questions && (
            <Section title="Long-Tail Questions" icon={MessageSquare}>
              <ContentBlock>
                <p className="text-neutral-700 mb-6 leading-relaxed">
                  These longer queries reflect specific concerns and often appear in Google's "People also ask" section. 
                  Use these exact phrases as blog post titles and video topics.
                </p>
              </ContentBlock>
              
              <div className="grid md:grid-cols-2 gap-4">
                {data.long_tail_questions.map((item, index) => (
                  <QuestionCard
                    key={index}
                    question={item.question}
                    context={item.context}
                    intent={item.intent}
                  />
                ))}
              </div>
            </Section>
          )}

          {/* Video Title Ideas */}
          {data.video_title_ideas && (
            <Section title="Video Content Strategy" icon={Youtube}>
              <ContentBlock>
                <p className="text-neutral-700 mb-6 leading-relaxed">
                  Strategic video titles that align with search behavior and YouTube best practices. 
                  These titles are optimized for both YouTube search and Google discovery.
                </p>
              </ContentBlock>
              
              <div className="space-y-4">
                {data.video_title_ideas.map((item, index) => (
                  <VideoTitleCard
                    key={index}
                    title={item.title}
                    strategy={item.strategy}
                    targetKeywords={item.target_keywords}
                    contentFocus={item.content_focus}
                  />
                ))}
              </div>
            </Section>
          )}

          {/* SEO Strategy Recommendations */}
          {data.seo_strategy && (
            <Section title="SEO Strategy &amp; Implementation" icon={Target}>
              <div className="space-y-4">
                {data.seo_strategy.map((insight, index) => (
                  <StrategyInsight
                    key={index}
                    category={insight.category}
                    recommendation={insight.recommendation}
                  />
                ))}
              </div>
            </Section>
          )}

          {/* Implementation Guidelines */}
          <ContentBlock className="bg-gradient-to-r from-neutral-50 to-green-50 border-green-200">
            <div className="flex items-start gap-3">
              <Lightbulb className="w-5 h-5 text-green-600 mt-1 flex-shrink-0" />
              <div>
                <h3 className="text-lg font-semibold text-neutral-900 mb-3">Implementation Tips</h3>
                <div className="space-y-2 text-neutral-700">
                  <p className="text-sm">
                    <strong>Content Calendar:</strong> Use 2-3 high-volume keywords per week as primary content themes
                  </p>
                  <p className="text-sm">
                    <strong>Blog Strategy:</strong> Answer one long-tail question per blog post with comprehensive, local context
                  </p>
                  <p className="text-sm">
                    <strong>Video Optimization:</strong> Include exact keyword phrases in titles, descriptions, and first 15 seconds of video
                  </p>
                  <p className="text-sm">
                    <strong>Local SEO:</strong> Optimize Google Business Profile and local citations with these exact search terms
                  </p>
                </div>
              </div>
            </div>
          </ContentBlock>
        </>
      )}
    </div>
  );
};

export default SeoYouTubeDetail;