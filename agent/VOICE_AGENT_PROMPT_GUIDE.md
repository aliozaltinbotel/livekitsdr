# Voice Agent Prompt Engineering Guide

This document explains the best practices applied to the Jamie voice agent prompt for optimal performance with LiveKit.

## Key Improvements Applied

### 1. State Machine Architecture
The prompt now uses a clear state machine with 7 distinct states:
- **STATE 1**: Greeting & consent
- **STATE 2**: Name collection
- **STATE 3**: Phone collection (with country code validation)
- **STATE 4**: Email collection
- **STATE 5**: Value proposition
- **STATE 6**: Demo scheduling
- **STATE 7**: Closing

### 2. Voice-Specific Optimizations

#### Natural Speech Patterns
- Removed all "processing" language ("let me check", "one moment")
- Uses immediate responses to maintain conversation flow
- Natural transitions between topics

#### Interruption Handling
- Clear instruction to stop immediately when interrupted
- Resume gracefully after interruption
- No repetition of completed information

#### Pacing & Clarity
- Chunks phone numbers for clarity: "+1... 555... 123... 4567"
- Uses NATO phonetic alphabet for spelling
- Moderate speaking pace with natural pauses

### 3. Comprehensive Edge Case Handling

#### Phone Number Collection
- **Country code enforcement**: Explicitly asks for country code
- **Format flexibility**: Accepts various input formats
- **Validation**: Checks digit count
- **Fallback**: After 2 attempts, proceeds with partial info
- **Examples**: Provides country code examples (+1 US, +44 UK)

#### Email Validation
- **Format checking**: Must contain @ and domain
- **Spelling assistance**: NATO alphabet for complex addresses
- **Domain shortcuts**: Auto-completes "gmail" to "gmail.com"
- **Confirmation**: Always spells back the full address

#### Name Handling
- **Nickname support**: Asks preference for formal vs casual
- **Multiple names**: Clarifies which to use
- **No name given**: Graceful fallback prompt

### 4. Error Recovery Strategies

#### Three-Attempt Rule
1. First attempt: Simple repetition request
2. Second attempt: Asks for louder/slower speech
3. Third attempt: Offers alternative communication method

#### System Failure Handling
- Calendar errors: Offers manual scheduling
- Tool failures: Continues conversation naturally
- Never exposes technical errors to user

### 5. Conversation Flow Optimization

#### Information Architecture
1. Collect all data first
2. Verify each piece immediately
3. Present value prop only after data collection
4. Schedule demo as final step

#### Time Management
- 3-4 minute total call target
- 60-second value proposition
- Quick transitions between states
- No unnecessary elaboration

### 6. Voice Agent Best Practices

#### Confirmation Patterns
- Always repeat information back
- Use clear confirmation questions
- Chunk long information (phone numbers)
- Spell complex items

#### Natural Language
- Conversational tone throughout
- Contractions and casual language
- Personality-driven responses
- Contextual responses based on user tone

#### Objection Handling
- Pre-defined responses for common objections
- Pivots to understand user needs
- Alternative offers (10-min demo, email info)
- Never pushy or aggressive

### 7. Tool Integration Best Practices

#### Silent Tool Usage
- Calendar checks happen silently
- No "checking availability" announcements
- Seamless integration of results
- Natural error handling if tools fail

#### Fallback Behavior
- Manual scheduling if calendar fails
- Continue conversation without tool mentions
- Alternative contact methods offered

## Technical Considerations

### Speech Recognition Optimization
- Clear, simple vocabulary
- Avoids ambiguous phrases
- Repeats important information
- Uses context to disambiguate

### Response Generation
- Short, clear sentences
- One idea per utterance
- Natural pause points
- Conversation-appropriate length

### State Tracking
- Clear state transitions
- No backward navigation
- Progress tracking implicit
- Graceful state recovery

## Testing Recommendations

1. **Edge Case Testing**
   - International phone numbers
   - Complex email addresses
   - Uncommon names
   - System interruptions

2. **Flow Testing**
   - Complete happy path
   - Various objection paths
   - Error recovery scenarios
   - Tool failure cases

3. **Voice Quality Testing**
   - Different accents
   - Background noise
   - Poor connections
   - Fast/slow speakers

## Future Enhancements

1. **Multi-language Support**
   - Detect language preference
   - Adjust greeting accordingly
   - Maintain same structure

2. **Advanced Personalization**
   - Industry-specific value props
   - Regional customization
   - Time-of-day awareness

3. **Learning Integration**
   - Track successful patterns
   - Adjust scripts based on outcomes
   - A/B testing of phrases