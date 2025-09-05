import React, { useState } from 'react';
import { Card, Button, Badge, Tabs, TabsContent, TabsList, TabsTrigger } from './ui';
import { Copy, Download, RefreshCw, FileText, Instagram, Facebook, Linkedin, Twitter, Music, Youtube, Hash, PenTool, Mail } from 'lucide-react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001/api';

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

const ContentCard = ({ item, onCopy, onDownload }) => (
  <Card className="p-4 hover:shadow-md transition-shadow">
    <div className="flex items-start justify-between mb-2">
      <h4 className="font-medium text-sm text-neutral-800 line-clamp-2">{item.title}</h4>
      <div className="flex gap-1 ml-2">
        <Button 
          variant="ghost" 
          size="sm"
          onClick={() => onCopy(item.content)}
          className="h-8 w-8 p-0"
        >
          <Copy className="w-3 h-3" />
        </Button>
        <Button 
          variant="ghost" 
          size="sm"
          onClick={() => onDownload(item.name, item.content)}
          className="h-8 w-8 p-0"
        >
          <Download className="w-3 h-3" />
        </Button>
      </div>
    </div>
    
    <p className="text-xs text-neutral-600 mb-3 line-clamp-3">
      {item.content ? item.content.substring(0, 150) + '...' : 'No content preview available'}
    </p>
    
    <div className="flex items-center justify-between">
      <span className="text-xs text-neutral-500">{item.name}</span>
      {item.post_type && (
        <Badge variant="secondary" className="text-xs">
          {item.post_type}
        </Badge>
      )}
      {item.hashtags && (
        <span className="text-xs text-blue-600">#{item.hashtags.split('#').filter(Boolean).length - 1} tags</span>
      )}
    </div>
  </Card>
);

const PlatformTab = ({ platform, zipCode, onCopy, onDownload }) => {
  const [content, setContent] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hasGenerated, setHasGenerated] = useState(false);

  const generateContent = async () => {
    setLoading(true);
    setError('');
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/generate-platform-content/${platform}`,
        { zip_code: zipCode },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      // Extract content based on platform
      const platformKey = `${platform}_posts`;
      const fallbackKeys = ['instagram_posts', 'facebook_posts', 'tiktok_posts', 'linkedin_posts', 'youtube_shorts', 'twitter_posts', 'snapchat_posts', 'blog_posts', 'email_campaigns'];
      
      let newContent = response.data[platformKey] || 
                      response.data[fallbackKeys.find(key => response.data[key])] || 
                      [];
      
      setContent(prev => [...prev, ...newContent]);
      setHasGenerated(true);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate content');
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {content.map((item, index) => (
            <ContentCard 
              key={`${platform}-${index}`}
              item={item}
              onCopy={onCopy}
              onDownload={onDownload}
            />
          ))}
        </div>
      )}
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