"""Console-based educational quiz game inspired by 'Who Wants to Be a Millionaire'.
This game supports Arabic and English interfaces for 11th-grade physics topics.
"""

import argparse
import random
import re
import time
from typing import Dict, List, Optional

QUESTION_BANK = """// The following block contains all the topics and questions for the game.
// Parse this data carefully.

[--- ألصق هنا كامل المحتوى النصي من ملف الـ PDF الخاص بك. تأكد من أن كل موضوع له عنوان واضح والأسئلة مرقمة تحته مع تحديد الإجابة الصحيحة. ---]

**مثال على التنسيق الذي يجب أن يكون عليه المحتوى الملصق:**

**عنوان الموضوع الأول: الحركة الموجية**
1. السؤال: ما هي الظاهرة التي تحدث عندما تمر موجة صوتية من الهواء إلى الماء؟
    أ) انعكاس
    ب) انكسار (الإجابة الصحيحة)
    ج) حيود
    د) تداخل

2. السؤال: في الحركة التوافقية البسيطة، تكون سرعة الجسم أقصى ما يمكن عند...
    أ) موضع الاتزان (الإجابة الصحيحة)
    ب) أقصى إزاحة
    ج) منتصف المسافة بين الاتزان وأقصى إزاحة
    د) أي نقطة

**عنوان الموضوع الثاني: الضوء**
1. السؤال: لماذا يبدو حمام السباحة أقل عمقًا مما هو عليه في الواقع؟
    أ) بسبب انعكاس الضوء
    ب) بسبب انكسار الضوء (الإجابة الصحيحة)
    ج) بسبب حيود الضوء
    د) بسبب تشتت الضوء
"""

TRANSLATION_MAP: Dict[str, str] = {
    "الحركة الموجية": "Wave Motion",
    "ما هي الظاهرة التي تحدث عندما تمر موجة صوتية من الهواء إلى الماء؟": "What phenomenon occurs when a sound wave travels from air to water?",
    "انعكاس": "Reflection",
    "انكسار": "Refraction",
    "حيود": "Diffraction",
    "تداخل": "Interference",
    "في الحركة التوافقية البسيطة، تكون سرعة الجسم أقصى ما يمكن عند...": "In simple harmonic motion, the object's speed is greatest when...",
    "موضع الاتزان": "Equilibrium position",
    "أقصى إزاحة": "Maximum displacement",
    "منتصف المسافة بين الاتزان وأقصى إزاحة": "Halfway between equilibrium and maximum displacement",
    "أي نقطة": "Any point",
    "الضوء": "Light",
    "لماذا يبدو حمام السباحة أقل عمقًا مما هو عليه في الواقع؟": "Why does a swimming pool appear shallower than it really is?",
    "بسبب انعكاس الضوء": "Because of the reflection of light",
    "بسبب انكسار الضوء": "Because of the refraction of light",
    "بسبب حيود الضوء": "Because of the diffraction of light",
    "بسبب تشتت الضوء": "Because of the dispersion of light",
}

LANGUAGE_AR = "ar"
LANGUAGE_EN = "en"


def translate_text(text: str) -> str:
    """Translate Arabic text to English using the predefined map."""
    return TRANSLATION_MAP.get(text.strip(), text.strip())


def parse_question_bank(text: str) -> List[Dict[str, object]]:
    """Parse the question bank text into a structured list of topics and questions."""
    topics: List[Dict[str, object]] = []
    topic_pattern = re.compile(
        r"\*\*عنوان الموضوع.*?:\s*(.*?)\*\*(.*?)(?=\*\*عنوان الموضوع|\Z)",
        re.DOTALL,
    )
    question_pattern = re.compile(
        r"(\d+)\.\s*السؤال:\s*(.*?)\n\s*أ\)\s*(.*?)\n\s*ب\)\s*(.*?)\n\s*ج\)\s*(.*?)\n\s*د\)\s*(.*?)(?=\n\s*\d+\.|\Z)",
        re.DOTALL,
    )

    for topic_name, content in topic_pattern.findall(text):
        cleaned_topic = topic_name.strip()
        questions: List[Dict[str, object]] = []
        for (_, question_text, opt_a, opt_b, opt_c, opt_d) in question_pattern.findall(content):
            raw_options = [opt_a, opt_b, opt_c, opt_d]
            options: List[str] = []
            correct_index = None
            for idx, option in enumerate(raw_options):
                option_clean = option.strip()
                if "الإجابة الصحيحة" in option_clean:
                    option_clean = re.sub(r"\s*\(.*?الإجابة.*?\)", "", option_clean).strip()
                    correct_index = idx
                options.append(option_clean)
            if correct_index is None:
                continue
            questions.append(
                {
                    "question": question_text.strip(),
                    "options": options,
                    "correct_index": correct_index,
                }
            )
        if questions:
            topics.append({"topic": cleaned_topic, "questions": questions})
    return topics


def show_welcome_screen(delay: bool = True) -> None:
    """Display the welcome screen with the required text."""
    print("من سيربح المليون")
    print("EduDream School")
    print("إعداد الأستاذ/ إسلام فارس")
    if delay:
        time.sleep(3)
    print()


def choose_language(preselection: Optional[str] = None) -> str:
    """Prompt the user to choose between Arabic and English."""
    if preselection in {LANGUAGE_AR, LANGUAGE_EN}:
        if preselection == LANGUAGE_AR:
            print("تم اختيار اللغة: عربي")
        else:
            print("Language selected: English")
        return preselection

    while True:
        print("اختر اللغة / Choose a language:")
        print("1. عربي")
        print("2. English")
        choice = input("> ").strip()
        if choice == "1":
            return LANGUAGE_AR
        if choice == "2":
            return LANGUAGE_EN
        print("اختيار غير صالح. حاول مرة أخرى. / Invalid selection. Try again.")
        print()


def resolve_topic_preselection(topics: List[Dict[str, object]], identifier: str) -> Optional[Dict[str, object]]:
    """Match a topic using a numeric index or its Arabic/English name."""
    if not identifier:
        return None

    identifier = identifier.strip()
    if not identifier:
        return None

    if identifier.isdigit():
        index = int(identifier) - 1
        if 0 <= index < len(topics):
            return topics[index]
        return None

    normalized = identifier.lower()
    for topic in topics:
        arabic_name = topic["topic"].strip()
        english_name = translate_text(arabic_name).strip()
        if normalized in {arabic_name.lower(), english_name.lower()}:
            return topic
    return None


def format_topic_name(topic: Dict[str, object], language: str) -> str:
    """Return the topic name in the chosen language for display."""
    return topic["topic"] if language == LANGUAGE_AR else translate_text(topic["topic"])


def choose_topic(
    topics: List[Dict[str, object]],
    language: str,
    preselection: Optional[str] = None,
) -> Dict[str, object]:
    """Display topics and let the user choose one based on the selected language."""
    if preselection:
        matched_topic = resolve_topic_preselection(topics, preselection)
        if matched_topic:
            display_name = format_topic_name(matched_topic, language)
            if language == LANGUAGE_AR:
                print(f"تم اختيار الموضوع: {display_name}")
            else:
                print(f"Topic selected: {display_name}")
            return matched_topic
        else:
            fallback_message = (
                "لم يتم العثور على الموضوع المحدد. سيتم عرض قائمة المواضيع للاختيار منها."
                if language == LANGUAGE_AR
                else "Unable to match the requested topic. Displaying the topic list instead."
            )
            print(fallback_message)
            print()

    while True:
        print("اختر موضوعًا:" if language == LANGUAGE_AR else "Select a topic:")
        for idx, topic in enumerate(topics, start=1):
            display_name = format_topic_name(topic, language)
            print(f"{idx}. {display_name}")
        choice = input("> ").strip()
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(topics):
                return topics[index]
        print("الرجاء اختيار رقم صالح." if language == LANGUAGE_AR else "Please choose a valid number.")
        print()


def ask_questions(
    topic: Dict[str, object],
    language: str,
    rng: Optional[random.Random] = None,
) -> None:
    """Run the quiz for the selected topic with language-specific prompts."""
    questions = topic["questions"]
    if rng is None:
        shuffled_questions = random.sample(questions, k=len(questions))
    else:
        shuffled_questions = rng.sample(questions, k=len(questions))

    for number, question in enumerate(shuffled_questions, start=1):
        prompt_question = question["question"]
        options = question["options"]
        if language == LANGUAGE_EN:
            prompt_question = translate_text(prompt_question)
            translated_options = [translate_text(opt) for opt in options]
        else:
            translated_options = options

        print("-" * 50)
        print(
            f"السؤال {number}: {prompt_question}" if language == LANGUAGE_AR else f"Question {number}: {prompt_question}"
        )
        for idx, option_text in enumerate(translated_options, start=1):
            label = f"{idx}."
            print(f"{label} {option_text}")

        while True:
            prompt = "أدخل رقم الخيار (1-4): " if language == LANGUAGE_AR else "Enter the option number (1-4): "
            answer = input(prompt).strip()
            if answer.isdigit():
                answer_idx = int(answer) - 1
                if 0 <= answer_idx < len(options):
                    break
            print("إدخال غير صالح. حاول مرة أخرى." if language == LANGUAGE_AR else "Invalid input. Please try again.")

        correct_idx = question["correct_index"]
        is_correct = answer_idx == correct_idx
        correct_text = translated_options[correct_idx]
        if language == LANGUAGE_AR:
            print("إجابة صحيحة!" if is_correct else f"إجابة خاطئة، الإجابة الصحيحة هي: {correct_text}")
        else:
            print("Correct!" if is_correct else f"Incorrect, the right answer was {correct_text}.")
        print()

    closing_message = (
        "انتهت الأسئلة. أحسنت العمل!"
        if language == LANGUAGE_AR
        else "You have completed all questions. Great job!"
    )
    print(closing_message)


def parse_cli_args() -> argparse.Namespace:
    """Parse command-line arguments that control how the game runs."""
    parser = argparse.ArgumentParser(description="Play the Millionaire physics quiz.")
    parser.add_argument(
        "--language",
        choices=[LANGUAGE_AR, LANGUAGE_EN],
        help="Start the game directly in the specified language (ar or en).",
    )
    parser.add_argument(
        "--topic",
        help="Auto-select a topic by its number, Arabic name, or English name.",
    )
    parser.add_argument(
        "--skip-welcome",
        action="store_true",
        help="Skip the welcome screen delay.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Seed the question shuffling for a reproducible session.",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for the quiz game."""
    args = parse_cli_args()
    topics = parse_question_bank(QUESTION_BANK)
    if not topics:
        print("No questions found in the question bank.")
        return

    show_welcome_screen(delay=not args.skip_welcome)
    language = choose_language(args.language)
    chosen_topic = choose_topic(topics, language, preselection=args.topic)
    rng = random.Random(args.seed) if args.seed is not None else None
    ask_questions(chosen_topic, language, rng=rng)


if __name__ == "__main__":
    main()
