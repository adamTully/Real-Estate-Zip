import React, { useState } from 'react';
import { Copy, Download, RefreshCw, FileText, Instagram, Facebook, Linkedin, Twitter, Music, Youtube, Hash, PenTool, Mail } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

// Simple UI components
const Card = ({ children, className = "" }) => (
  <div className={`bg-white rounded-lg border border-neutral-200 shadow-sm ${className}`}>
    {children}
  </div>
);

const Button = ({ children, onClick, disabled, variant = "default", size = "default", className = "" }) => {
  const baseClasses = "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none";
  const variantClasses = {
    default: "bg-primary text-primary-foreground hover:bg-primary/90 bg-blue-600 text-white hover:bg-blue-700",
    outline: "border border-input hover:bg-accent hover:text-accent-foreground border-neutral-300 hover:bg-neutral-50",
    ghost: "hover:bg-accent hover:text-accent-foreground hover:bg-neutral-100"
  };
  const sizeClasses = {
    default: "h-10 py-2 px-4",
    sm: "h-8 px-3 text-sm"
  };
  
  return (
    <button 
      onClick={onClick}
      disabled={disabled}
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
    >
      {children}
    </button>
  );
};

const Badge = ({ children, variant = "default", className = "" }) => {
  const variantClasses = {
    default: "bg-primary text-primary-foreground bg-blue-600 text-white",
    secondary: "bg-secondary text-secondary-foreground bg-neutral-100 text-neutral-800"
  };
  
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${variantClasses[variant]} ${className}`}>
      {children}
    </span>
  );
};

// Simple Tabs implementation  
const Tabs = ({ children, defaultValue, className = "" }) => {
  const [activeTab, setActiveTab] = useState(defaultValue);
  
  return (
    <div className={`w-full ${className}`} data-active-tab={activeTab}>
      {React.Children.map(children, child => 
        React.cloneElement(child, { activeTab, setActiveTab })
      )}
    </div>
  );
};

const TabsList = ({ children, className = "", activeTab, setActiveTab }) => (
  <div className={`inline-flex h-10 items-center justify-center rounded-md bg-muted p-1 text-muted-foreground bg-neutral-100 ${className}`}>
    {React.Children.map(children, child => 
      React.cloneElement(child, { activeTab, setActiveTab })
    )}
  </div>
);

const TabsTrigger = ({ children, value, className = "", activeTab, setActiveTab }) => {
  const isActive = activeTab === value;
  return (
    <button
      onClick={() => setActiveTab(value)}
      className={`inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ${
        isActive 
          ? 'bg-background text-foreground shadow-sm bg-white text-neutral-900' 
          : 'hover:bg-background/80 hover:text-foreground hover:bg-white/50'
      } ${className}`}
    >
      {children}
    </button>
  );
};

const TabsContent = ({ children, value, className = "", activeTab }) => {
  if (activeTab !== value) return null;
  return (
    <div className={`mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ${className}`}>
      {children}
    </div>
  );
};

const PlatformIcon = ({ platform }) => {
  const icons = {
    instagram: Instagram,
    facebook: Facebook, 
    linkedin: Linkedin,
    twitter: Twitter,
    tiktok: Music,
    'youtube-shorts': Youtube,
    snapchat: Hash,
    blog: PenTool,
    email: Mail
  };
  const Icon = icons[platform] || FileText;
  return <Icon className="w-4 h-4" />;
};

// Content Row Component (Table Style)
const ContentRow = ({ item, onCopy, onDownload, onClick }) => (
  <div className="border border-neutral-200 rounded-lg hover:bg-neutral-50 transition-colors">
    <div 
      className="p-4 cursor-pointer" 
      onClick={() => {
        console.log('ContentRow clicked:', item); // Debug log
        onClick(item);
      }}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-start gap-4">
            <div className="flex-1">
              <h4 className="font-medium text-sm text-neutral-900 hover:text-blue-600 transition-colors mb-1">
                {item.title}
              </h4>
              <p className="text-xs text-neutral-600 line-clamp-2 mb-2">
                {item.content ? item.content.substring(0, 200) + '...' : 'No content preview available'}
              </p>
              <div className="flex items-center gap-4 text-xs text-neutral-500">
                <span>{item.name}</span>
                {item.post_type && (
                  <Badge variant="secondary" className="text-xs">
                    {item.post_type}
                  </Badge>
                )}
                {item.hashtags && (
                  <span className="text-blue-600">#{item.hashtags.split('#').filter(Boolean).length - 1} tags</span>
                )}
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex gap-1 ml-4">
          <Button 
            variant="ghost" 
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              console.log('Copy button clicked'); // Debug log
              onCopy(item.content);
            }}
            className="h-8 w-8 p-0"
            title="Copy content"
          >
            <Copy className="w-3 h-3" />
          </Button>
          <Button 
            variant="ghost" 
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              console.log('Download button clicked'); // Debug log
              onDownload(item.name, item.content);
            }}
            className="h-8 w-8 p-0"
            title="Download content"
          >
            <Download className="w-3 h-3" />
          </Button>
        </div>
      </div>
    </div>
  </div>
);

// Content Drawer Component
const ContentDrawer = ({ isOpen, onClose, item, onCopy, platformLabel }) => {
  if (!isOpen || !item) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Drawer */}
      <div className="absolute right-0 top-0 h-full w-full max-w-2xl bg-white shadow-xl transform transition-transform">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-neutral-200">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <PlatformIcon platform={platformLabel.toLowerCase().replace(/[^a-z]/g, '')} />
                <h2 className="text-lg font-semibold text-neutral-900">{platformLabel} Content</h2>
              </div>
              {item.post_type && (
                <Badge variant="secondary">{item.post_type}</Badge>
              )}
            </div>
            <Button variant="ghost" onClick={onClose} className="h-8 w-8 p-0">
              <span className="text-xl">&times;</span>
            </Button>
          </div>
          
          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {/* Title Section */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-neutral-500 uppercase tracking-wide">Title</h3>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => onCopy(item.title)}
                  className="text-xs gap-1 hover:bg-blue-50 hover:text-blue-600"
                >
                  <Copy className="w-3 h-3" />
                  Copy Title
                </Button>
              </div>
              <div 
                className="p-4 bg-neutral-50 rounded-lg border cursor-pointer hover:bg-blue-50 transition-colors group"
                onClick={() => onCopy(item.title)}
                title="Click to copy title"
              >
                <p className="text-neutral-900 font-medium group-hover:text-blue-600 transition-colors">
                  {item.title}
                </p>
              </div>
            </div>

            {/* Content Section */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-neutral-500 uppercase tracking-wide">Content</h3>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => onCopy(item.content)}
                  className="text-xs gap-1 hover:bg-blue-50 hover:text-blue-600"
                >
                  <Copy className="w-3 h-3" />
                  Copy Content
                </Button>
              </div>
              <div 
                className="p-4 bg-neutral-50 rounded-lg border cursor-pointer hover:bg-blue-50 transition-colors group min-h-[200px]"
                onClick={() => onCopy(item.content)}
                title="Click to copy content"
              >
                <pre className="text-neutral-900 whitespace-pre-wrap font-sans text-sm leading-relaxed group-hover:text-blue-600 transition-colors">
                  {item.content}
                </pre>
              </div>
            </div>

            {/* Hashtags/Additional Info */}
            {item.hashtags && (
              <div className="space-y-2">
                <h3 className="text-sm font-medium text-neutral-500 uppercase tracking-wide">Hashtags</h3>
                <div 
                  className="p-4 bg-blue-50 rounded-lg border cursor-pointer hover:bg-blue-100 transition-colors"
                  onClick={() => onCopy(item.hashtags)}
                  title="Click to copy hashtags"
                >
                  <p className="text-blue-800 text-sm">{item.hashtags}</p>
                </div>
              </div>
            )}

            {/* Hook (for social platforms) */}
            {item.hook && (
              <div className="space-y-2">
                <h3 className="text-sm font-medium text-neutral-500 uppercase tracking-wide">Hook</h3>
                <div 
                  className="p-4 bg-green-50 rounded-lg border cursor-pointer hover:bg-green-100 transition-colors"
                  onClick={() => onCopy(item.hook)}
                  title="Click to copy hook"
                >
                  <p className="text-green-800 text-sm font-medium">{item.hook}</p>
                </div>
              </div>
            )}

            {/* Visual Concept */}
            {item.visual_concept && (
              <div className="space-y-2">
                <h3 className="text-sm font-medium text-neutral-500 uppercase tracking-wide">Visual Concept</h3>
                <div className="p-4 bg-purple-50 rounded-lg border">
                  <p className="text-purple-800 text-sm">{item.visual_concept}</p>
                </div>
              </div>
            )}
          </div>
          
          {/* Footer */}
          <div className="border-t border-neutral-200 p-6 bg-neutral-50">
            <div className="flex items-center justify-between">
              <span className="text-sm text-neutral-500">{item.name}</span>
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  onClick={() => onCopy(item.content)}
                  className="gap-2"
                >
                  <Copy className="w-4 h-4" />
                  Copy All
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => {
                    const blob = new Blob([item.content], { type: 'text/plain' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = item.name;
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                  className="gap-2"
                >
                  <Download className="w-4 h-4" />
                  Download
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const PlatformTab = ({ platform, zipCode, onCopy, onDownload }) => {
  const [content, setContent] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hasGenerated, setHasGenerated] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressText, setProgressText] = useState('');
  const [selectedItem, setSelectedItem] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const openDrawer = (item) => {
    console.log('Opening drawer for item:', item); // Debug log
    setSelectedItem(item);
    setIsDrawerOpen(true);
  };

  const closeDrawer = () => {
    console.log('Closing drawer'); // Debug log
    setIsDrawerOpen(false);
    setSelectedItem(null);
  };

  // Load content from localStorage on component mount
  React.useEffect(() => {
    const savedContent = localStorage.getItem(`content_${platform}_${zipCode}`);
    if (savedContent) {
      try {
        const parsedContent = JSON.parse(savedContent);
        setContent(parsedContent);
        setHasGenerated(parsedContent.length > 0);
      } catch (error) {
        console.error('Error loading saved content:', error);
      }
    }
  }, [platform, zipCode]);

  // Save content to localStorage whenever it changes
  React.useEffect(() => {
    if (content.length > 0) {
      localStorage.setItem(`content_${platform}_${zipCode}`, JSON.stringify(content));
    }
  }, [content, platform, zipCode]);

  const generateContent = async () => {
    setLoading(true);
    setError('');
    setProgress(0);
    setProgressText('Initializing...');
    
    let progressInterval;
    
    try {
      // Simulate progress updates
      const progressSteps = [
        { percent: 10, text: 'Connecting to AI...' },
        { percent: 25, text: 'Analyzing market data...' },
        { percent: 50, text: 'Generating content...' },
        { percent: 75, text: 'Optimizing for platform...' },
        { percent: 90, text: 'Finalizing posts...' }
      ];

      // Start progress simulation
      let currentStep = 0;
      progressInterval = setInterval(() => {
        if (currentStep < progressSteps.length) {
          setProgress(progressSteps[currentStep].percent);
          setProgressText(progressSteps[currentStep].text);
          currentStep++;
        }
      }, 800);

      const token = localStorage.getItem('auth_token');
      
      if (!token) {
        clearInterval(progressInterval);
        setError('Authentication required. Please log in again.');
        return;
      }
      
      const response = await axios.post(
        `${API}/generate-platform-content/${platform}`,
        { zip_code: zipCode },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      clearInterval(progressInterval);
      setProgress(100);
      setProgressText('Content generated successfully!');
      
      // Extract content based on platform
      const platformKey = `${platform}_posts`;
      const fallbackKeys = ['instagram_posts', 'facebook_posts', 'tiktok_posts', 'linkedin_posts', 'youtube_shorts', 'twitter_posts', 'snapchat_posts', 'blog_posts', 'email_campaigns'];
      
      console.log('Platform:', platform); // Debug log
      console.log('Platform key:', platformKey); // Debug log
      console.log('Response data keys:', Object.keys(response.data)); // Debug log
      console.log('Response data:', response.data); // Debug log
      
      let newContent = response.data[platformKey] || 
                      response.data[fallbackKeys.find(key => response.data[key])] || 
                      [];
      
      console.log('Extracted content:', newContent); // Debug log
      console.log('Content length:', newContent.length); // Debug log
      
      setContent(prev => {
        const updatedContent = [...prev, ...newContent];
        console.log('Updated content state:', updatedContent); // Debug log
        return updatedContent;
      });
      setHasGenerated(true);
      
      // Reset progress after short delay
      setTimeout(() => {
        setProgress(0);
        setProgressText('');
      }, 2000);
      
    } catch (err) {
      // Clear interval on any error
      if (progressInterval) {
        clearInterval(progressInterval);
      }
      
      if (err.response?.status === 401) {
        setError('Your session has expired. Please log out and log back in.');
      } else {
        setError(err.response?.data?.detail || 'Failed to generate content');
      }
      
      setProgress(0);
      setProgressText('');
    } finally {
      setLoading(false);
    }
  };

  const platformLabels = {
    instagram: 'Instagram',
    facebook: 'Facebook', 
    linkedin: 'LinkedIn',
    twitter: 'Twitter/X',
    tiktok: 'TikTok',
    'youtube-shorts': 'YouTube Shorts',
    snapchat: 'Snapchat',
    blog: 'Blog Posts',
    email: 'Email Campaigns'
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <PlatformIcon platform={platform} />
          <h3 className="text-lg font-semibold">{platformLabels[platform] || platform}</h3>
          {content.length > 0 && (
            <Badge variant="secondary">{content.length} items</Badge>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          {content.length > 0 && (
            <Button 
              onClick={() => {
                setContent([]);
                setHasGenerated(false);
                localStorage.removeItem(`content_${platform}_${zipCode}`);
              }}
              variant="outline"
              size="sm"
              className="text-red-600 hover:text-red-700"
            >
              Clear
            </Button>
          )}
          
          <Button 
            onClick={generateContent}
            disabled={loading}
            className="gap-2"
            variant={hasGenerated ? "outline" : "default"}
          >
            {loading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <PlatformIcon platform={platform} />
            )}
            {loading ? 'Generating...' : hasGenerated ? 'Generate More' : 'Generate Content'}
          </Button>
        </div>
      </div>

      {/* Progress Bar */}
      {loading && (
        <Card className="p-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-neutral-600">{progressText}</span>
              <span className="text-neutral-900 font-medium">{progress}%</span>
            </div>
            <div className="w-full bg-neutral-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <div className="text-xs text-neutral-500 text-center">
              ⚡ Generating {platformLabels[platform]} content using AI...
            </div>
          </div>
        </Card>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {content.length === 0 && !loading && (
        <div className="text-center py-12">
          <PlatformIcon platform={platform} />
          <h4 className="text-lg font-medium text-neutral-700 mt-2">No content generated yet</h4>
          <p className="text-sm text-neutral-500 mt-1">Click "Generate Content" to create {platformLabels[platform]} posts</p>
        </div>
      )}

      {content.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between border-b border-neutral-200 pb-2 mb-4">
            <h4 className="text-sm font-medium text-neutral-700">Generated Content</h4>
            <span className="text-xs text-neutral-500">{content.length} items</span>
          </div>
          {content.map((item, index) => {
            console.log(`Rendering item ${index}:`, item); // Debug log
            return (
              <ContentRow 
                key={`${platform}-${index}`}
                item={item}
                onCopy={onCopy}
                onDownload={onDownload}
                onClick={(clickedItem) => {
                  console.log('Item clicked in map:', clickedItem); // Debug log
                  openDrawer(clickedItem);
                }}
              />
            );
          })}
        </div>
      )}

      {/* Content Drawer */}
      <ContentDrawer 
        isOpen={isDrawerOpen}
        onClose={closeDrawer}
        item={selectedItem}
        onCopy={onCopy}
        platformLabel={platformLabels[platform]}
      />
    </div>
  );
};

const ContentAssetsPlatform = ({ zipCode, analysisData }) => {
  const [copiedText, setCopiedText] = useState('');

  const platforms = [
    'instagram',
    'facebook', 
    'linkedin',
    'twitter',
    'tiktok',
    'youtube-shorts',
    'snapchat',
    'blog',
    'email'
  ];

  const handleCopy = async (content) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedText(content.substring(0, 50) + '...');
      setTimeout(() => setCopiedText(''), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const handleDownload = (filename, content) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!zipCode) {
    return (
      <div className="text-center py-12">
        <FileText className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-neutral-700">No ZIP Code Assigned</h3>
        <p className="text-sm text-neutral-500 mt-1">You need an assigned territory to generate platform content</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-neutral-900">Content Generation Hub</h1>
        <p className="text-neutral-600">Generate platform-specific content for ZIP {zipCode}</p>
        {copiedText && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-2 max-w-md mx-auto">
            <p className="text-sm text-green-700">Copied: {copiedText}</p>
          </div>
        )}
      </div>

      <Tabs defaultValue="instagram" className="w-full">
        <TabsList className="grid w-full grid-cols-5 lg:grid-cols-9 gap-1">
          {platforms.map(platform => (
            <TabsTrigger key={platform} value={platform} className="flex items-center gap-1 text-xs">
              <PlatformIcon platform={platform} />
              <span className="hidden sm:inline">{platform === 'youtube-shorts' ? 'YT' : platform.charAt(0).toUpperCase() + platform.slice(1)}</span>
            </TabsTrigger>
          ))}
        </TabsList>

        {platforms.map(platform => (
          <TabsContent key={platform} value={platform} className="mt-6">
            <PlatformTab 
              platform={platform}
              zipCode={zipCode}
              onCopy={handleCopy}
              onDownload={handleDownload}
            />
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
};

export default ContentAssetsPlatform;