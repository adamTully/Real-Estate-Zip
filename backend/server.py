@@
     async def generate_buyer_migration_intel(self, zip_code: str, location_info: Dict) -> Dict[str, Any]:
         city_name = location_info.get('city', 'Unknown')
         state_name = location_info.get('state', 'Unknown')
         try:
-            prompt = f"""Act as a real estate market analyst. I'm a Realtor in {city_name}, {state_name}. Based on the latest migration patterns, tell me: where most of the buyers relocating to {city_name} are coming from; why they're moving (cost of living, lifestyle, taxes, etc.); and what type of content should I be creating to attract those buyers. Include specific hooks, keywords, and video titles based on current trends.
-
-Please structure your response with clear sections and be specific with data, statistics, and actionable recommendations."""
+            prompt = f"""
+Act as a real estate market analyst. I'm a Realtor in {city_name}, {state_name} (ZIP {zip_code}).
+
+Return your answer in clean, scannable Markdown with clear headings, subheadings, and lists. Use this exact structure:
+
+# Buyer Migration Intelligence – {city_name}, {state_name}
+
+## Market Overview
+- 2-4 sentences summarizing notable migration dynamics and housing context.
+
+## Where Buyers Are Coming From
+- Bullet list of top feeder cities/metros/states with brief reasons (1 line each)
+- If relevant, include a simple table:
+
+| Origin | Share/Trend | Note |
+| --- | --- | --- |
+| City A | Rising | Lower cost, job inflows |
+| City B | Stable | Lifestyle upgrade |
+
+## Why They're Moving
+- Bullet list of top motivations (cost of living, schools, taxes, commute, lifestyle, climate, etc.) with practical implications for messaging
+
+## Content Strategy To Attract These Buyers
+### Hooks (5-7)
+- Short, thumb-stopping hooks tailored to {city_name}
+
+### SEO Keywords (10-15)
+- Comma-separated list or bullets of local, high-intent terms
+
+### Video Title Ideas (5-10)
+- YouTube-style titles optimized for search and CTR
+
+## Quick Actions (3-5)
+- Actionable next steps you recommend a local agent takes this week
+
+Be specific, professional, and avoid fluff. Use lists where possible. Keep table simple and valid Markdown. """
             response_text = await self._safe_send(prompt)
@@
             return {
                 "summary": f"Migration analysis for {city_name}, {state_name} completed with real market data",
                 "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                 "analysis_content": response_text,
                 "generated_with": "ChatGPT GPT-5",
                 "timestamp": datetime.utcnow().isoformat()
             }
@@
             return {
                 "summary": f"Migration analysis for {city_name}, {state_name} (fallback mode)",
                 "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                 "analysis_content": "Real-time analysis temporarily unavailable. Please try again.",
                 "error": str(e)
             }