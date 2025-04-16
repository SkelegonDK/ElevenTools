# ElevenLabs Text-to-Speech Advanced Prompting Guide

## Introduction

This guide will help you create effective and nuanced prompts for ElevenLabs AI text-to-speech synthesis. We'll cover techniques for adding pauses, conveying emotions, controlling pacing, ensuring proper pronunciation, and using advanced methods for emphasis and emotional context.

---

## Pauses

### Syntax-Based Pauses

The most consistent way to introduce pauses is by using the `<break>` tag. This works across all ElevenLabs models.

```
"Give me one second to think about it." <break time="1.5s" /> "Yes, that would work."
```

- Use `time` attribute to specify pause duration in seconds (up to 3 seconds)
- Available in Speech Synthesis and via API (not yet in Projects)
- Avoid excessive use of break tags to prevent instability

### Alternative Pause Methods

These methods are less consistent but can be useful in certain situations:

1. Dashes:

```
"It - is - getting late."
```

2. Multiple dashes for longer pauses:

```
"Let me think -- -- I've got it!"
```

3. Ellipsis (adds hesitation):

```
"I... yeah, I guess so..."
```

---

## Pronunciation

**Note:** This feature is currently only supported by the "Eleven English V1" and "Eleven Turbo V2" models.

Use the `<phoneme>` tag to specify pronunciation using IPA or CMU Arpabet:

### IPA Example:

```
<phoneme alphabet="ipa" ph="ˈæktʃuəli">actually</phoneme>
```

### CMU Arpabet Example:

```
<phoneme alphabet="cmu-arpabet" ph="AE1 K CH UW0 AH0 L IY0">actually</phoneme>
```

**Important:**
- Apply `<phoneme>` tags to individual words
- Include lexical stress in multi-syllable words (0 = no stress, 1 = primary stress, 2 = secondary stress)

---

## Emotion and Context

To convey specific emotions or context without having the text-to-speech model actually speak the emotional description, use the `<emotional context>` tag:

```
"I LOVE this book <passionate happiness>"
```

**Note:** The effectiveness of emotional context tags can vary depending on the specific voice model being used. Experiment with different emotions and contexts to find what works best for each voice.

---

## Emphasis and Intonation

### Using All Caps for Emphasis

To add emphasis to specific words and create more dramatic intonation, use all capital letters strategically:

```
"YOU did this, just YOU, ALL by yourself"
```

This technique creates "peaks and valleys" in the sentence, making it sound more dynamic and engaging. Be careful not to overuse this technique, as emphasizing too many words can reduce its effectiveness.

### Enhanced Question Emphasis

For questions that require heavier emphasis, add one or two additional question marks:

```
"Are you REALLY sure about that???"
```

This can help the AI model recognize the importance or intensity of the question and adjust its intonation accordingly.

---

## Pacing

Control pacing by using descriptive language:

```
"I wish you were right, I truly do, but you're not," he said slowly.
```

**Tip:** For voice cloning, using a single long sample may yield better results than multiple shorter samples.

---

## Best Practices

1. Experiment with different techniques to find what works best for your specific use case and the chosen voice model
2. Use a combination of syntax-based pauses, emotional context tags, and strategic capitalization for natural and expressive speech
3. When using pronunciation tags, always include lexical stress for multi-syllable words
4. For emotion and pacing, write in a style similar to narrative prose, but use the `<emotional context>` tags to guide the AI without speaking the emotions directly
5. Create "peaks and valleys" in your sentences using capitalization and punctuation for more dynamic and engaging speech
6. Test your prompts with different voices to ensure consistency and effectiveness across various use cases

---

## Conclusion

Mastering ElevenLabs text-to-speech prompting requires practice, experimentation, and an understanding of the nuances of each technique. Use this guide as a starting point, and don't be afraid to combine different methods to achieve the desired output. Remember that different voices and models may respond differently to various prompting techniques, so always test your prompts thoroughly before finalizing your project.