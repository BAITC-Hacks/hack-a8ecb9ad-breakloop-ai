import re
from pathlib import Path

FAQ_FILE = Path(__file__).parent / "faq.txt"

# слова, которые не несут смысла и не помогают матчить
STOP_WORDS = {
    "и", "в", "во", "на", "не", "что", "как", "когда", "где", "какой",
    "какая", "какие", "у", "нас", "мы", "вы", "это", "а", "но", "или",
    "по", "за", "с", "со", "к", "ко", "о", "об", "про", "для", "до",
    "the", "a", "an", "is", "are", "what", "when", "where", "how",
}


def load_faq(path: Path) -> list[tuple[str, str, set[str]]]:
    """Читает faq.txt и возвращает список (вопрос, ответ, ключевые_слова)."""
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"\n\s*\n", text.strip())
    items = []
    for block in blocks:
        q_match = re.search(r"^Q:\s*(.+)$", block, re.MULTILINE)
        a_match = re.search(r"^A:\s*(.+)$", block, re.MULTILINE | re.DOTALL)
        if not q_match or not a_match:
            continue
        question = q_match.group(1).strip()
        answer = " ".join(a_match.group(1).split())
        keywords = extract_keywords(question + " " + answer)
        items.append((question, answer, keywords))
    return items


def extract_keywords(text: str) -> set[str]:
    words = re.findall(r"[а-яёa-z0-9]+", text.lower())
    return {w for w in words if w not in STOP_WORDS and len(w) > 2}


def stem(word: str) -> str:
    """Очень грубый стемминг: обрезаем типичные окончания."""
    for suffix in ("ами", "ями", "ов", "ев", "ые", "ая", "ое", "ий",
                   "ый", "ой", "ах", "ях", "ам", "ям", "у", "ю", "а",
                   "я", "ы", "и", "е", "о", "ь"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def score(user_words: set[str], faq_keywords: set[str]) -> int:
    user_stems = {stem(w) for w in user_words}
    faq_stems = {stem(w) for w in faq_keywords}
    return len(user_stems & faq_stems)


def find_answer(query: str, faq, min_score: int = 1):
    user_words = extract_keywords(query)
    if not user_words:
        return None
    best = None
    best_score = 0
    for question, answer, keywords in faq:
        s = score(user_words, keywords)
        if s > best_score:
            best_score = s
            best = (question, answer)
    if best_score < min_score:
        return None
    return best


def main():
    faq = load_faq(FAQ_FILE)
    print("FAQ-бот репетиции. Напиши вопрос или 'выход' для выхода.\n")
    while True:
        try:
            query = input("Ты: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not query:
            continue
        if query.lower() in {"выход", "exit", "quit"}:
            break
        result = find_answer(query, faq)
        if result is None:
            print("Бот: не знаю\n")
        else:
            _, answer = result
            print(f"Бот: {answer}\n")


if __name__ == "__main__":
    main()