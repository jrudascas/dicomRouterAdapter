from exceptions.Exceptions import AssociationException
import unittest


class UnitTest(unittest.TestCase):

    def test_str_without_message(self):
        try:
            raise AssociationException
        except Exception as e:
            self.assertEqual(e.__str__(), 'AssociationException has been raised')

    def test_str_with_message(self):
        try:
            raise AssociationException('MessageTest')
        except Exception as e:
            self.assertEqual(e.__str__(), 'AssociationException, MessageTest')


if __name__ == '__main__':
    unittest.main()