import unittest

from lxml import html

from grabber import Category


class TestGrabber(unittest.TestCase):
    def test_category(self):
        self.assertEqual('foo'.upper(), 'FOO')
        cate_li = """
        <li>
			<span class="item-title"><a href="/news/vac">
			Вакансии</a>
		</span>
				        					<dl><dt>
				Кол-во материалов:</dt>
				<dd>84</dd>
			</dl>
	</li>
        """
        li = html.fromstring(cate_li)
        domain = "http://fit.nsu.ru"
        try:
            cat = Category(domain, li, None, db=False)
            cat()
            self.assertGreater(len(cat.items), 0)
        except Exception:
            self.fail("Exception")

        self.fail()




if __name__ == '__main__':
    unittest.main()
