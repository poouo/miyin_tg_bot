import io
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from PIL import Image

from apps.api.app.services.moderation.captcha_image import (
    CAPTCHA_ALPHABET,
    CAPTCHA_LENGTH,
    IMAGE_HEIGHT,
    IMAGE_WIDTH,
    build_letter_options,
    generate_captcha_text,
    render_captcha_gif,
)
from apps.api.app.services.moderation.join_verification import (
    challenge_failure_reason,
    is_challenge_answer_correct,
)


def _challenge(answer: str, *, passed: bool = False, seconds_left: int = 60):
    return SimpleNamespace(
        answer=answer,
        passed=passed,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=seconds_left),
    )


class CaptchaTextTests(unittest.TestCase):
    def test_text_is_four_distinct_letters_from_alphabet(self):
        for _ in range(200):
            text = generate_captcha_text()
            self.assertEqual(len(text), CAPTCHA_LENGTH)
            self.assertEqual(len(set(text)), CAPTCHA_LENGTH)
            self.assertTrue(set(text) <= set(CAPTCHA_ALPHABET))

    def test_options_contain_answer_and_look_like_answers(self):
        for _ in range(300):
            answer = generate_captcha_text()
            options = build_letter_options(answer)
            self.assertEqual(len(options), 4)
            self.assertEqual(len(set(options)), 4)
            self.assertIn(answer, options)
            for option in options:
                self.assertEqual(len(option), CAPTCHA_LENGTH)
                # distractors must not be recognisable by a repeated letter
                self.assertEqual(len(set(option)), CAPTCHA_LENGTH)
                self.assertLessEqual(len(option.encode()), 8)  # fits callback_data


class CaptchaImageTests(unittest.TestCase):
    def test_gif_is_animated_and_reasonably_small(self):
        data = render_captcha_gif("KRDM")
        image = Image.open(io.BytesIO(data))
        self.assertEqual(image.format, "GIF")
        self.assertEqual(image.size, (IMAGE_WIDTH, IMAGE_HEIGHT))
        self.assertTrue(image.is_animated)
        self.assertGreaterEqual(image.n_frames, 8)
        self.assertLess(len(data), 600 * 1024)

    def test_frames_differ_from_each_other(self):
        image = Image.open(io.BytesIO(render_captcha_gif("WXTN")))
        image.seek(0)
        first = image.convert("RGB").tobytes()
        image.seek(5)
        self.assertNotEqual(first, image.convert("RGB").tobytes())


class CaptchaAnswerTests(unittest.TestCase):
    def test_answer_is_case_and_whitespace_insensitive(self):
        challenge = _challenge("KRDM")
        self.assertTrue(is_challenge_answer_correct(challenge, "KRDM"))
        self.assertTrue(is_challenge_answer_correct(challenge, " krdm "))

    def test_wrong_expired_or_used_answers_fail(self):
        self.assertFalse(is_challenge_answer_correct(_challenge("KRDM"), "KRDN"))
        self.assertFalse(is_challenge_answer_correct(_challenge("KRDM", seconds_left=-5), "KRDM"))
        self.assertFalse(is_challenge_answer_correct(_challenge("KRDM", passed=True), "KRDM"))
        self.assertFalse(is_challenge_answer_correct(None, "KRDM"))

    def test_failure_reason(self):
        self.assertEqual(challenge_failure_reason(_challenge("KRDM"), "ZZZZ"), "答案错误")
        self.assertEqual(challenge_failure_reason(_challenge("KRDM", seconds_left=-5), "KRDM"), "验证超时")

    def test_legacy_math_answers_still_work(self):
        self.assertTrue(is_challenge_answer_correct(_challenge("12"), "12"))
        self.assertFalse(is_challenge_answer_correct(_challenge("12"), "13"))


if __name__ == "__main__":
    unittest.main()
