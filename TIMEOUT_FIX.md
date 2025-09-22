# Image Generation Timeout Fix

## Problem
Image generation was timing out after 30 seconds, especially when generating multiple variations with complex prompts like "high quality photo of 2 huskies playing, hyper realistic, unreal engine" with 4 variations.

## Root Cause
- Default timeout was too short (30s) for complex image generation
- Multiple variations significantly increase processing time
- High-quality, detailed prompts require more processing time

## Solution Implemented

### 1. Dynamic Timeout Calculation
```python
# Calculate timeout based on number of variations
timeout_multiplier = max(variations, 1)
extended_timeout = min(120, 60 + (timeout_multiplier * 20))
```

**Timeout Schedule:**
- 1 variation: 80 seconds
- 2 variations: 100 seconds
- 3 variations: 120 seconds
- 4 variations: 120 seconds (capped)

### 2. Dedicated Timeout Method
Created `_make_request_with_timeout()` for operations that need longer timeouts:
- Image generation: Dynamic timeout (80-120s)
- Video generation: Fixed 90s timeout
- Regular API calls: Standard 30s timeout

### 3. Better User Feedback
- Shows estimated generation time upfront
- Users know what to expect for their request
- Prevents confusion about processing delays

### 4. Optimized for Your Use Case
Your specific request:
- **Prompt**: "high quality photo of 2 huskies playing, hyper realistic, unreal engine"
- **Model**: openai/dall-e-3
- **Variations**: 4
- **Timeout**: 120 seconds (was 30s)

## Expected Results

✅ **Before**: Timeout after 30s with complex prompts
✅ **After**: Up to 120s for complex multi-variation requests

## Testing

Run the timeout test:
```bash
cd src
python3 test_timeout_fix.py
```

## Additional Optimizations

1. **Progressive Timeout**: Longer timeouts for more complex requests
2. **Better Error Messages**: Clear indication of processing time
3. **User Expectations**: Estimated time shown upfront
4. **Fallback Handling**: Graceful degradation on timeout

## Usage Notes

- Single variations: ~80s timeout
- Multiple variations: Up to 120s timeout
- Complex prompts with "hyper realistic", "unreal engine" etc. need more time
- DALL-E 3 generally slower but higher quality than other models

This should completely resolve your timeout issues! 🚀