from mage_ai.data_preparation.models.block import Block
from mage_ai.data_preparation.models.pipeline import Pipeline
from mage_ai.data_preparation.models.variable import Variable, VariableType
from mage_ai.tests.base_test import TestCase
from pandas.util.testing import assert_frame_equal
import os
import pandas as pd
import shutil


class VariableTest(TestCase):
    def setUp(self):
        self.repo_path = os.getcwd() + '/test'
        if not os.path.exists(self.repo_path):
            os.mkdir(self.repo_path)
        return super().setUp()

    def tearDown(self):
        shutil.rmtree(self.repo_path)
        return super().tearDown()

    def test_write_and_read_data(self):
        pipeline = self.__create_pipeline('test pipeline 1')
        variable1 = Variable('var1', pipeline.dir_path, 'block1')
        variable2 = Variable('var2', pipeline.dir_path, 'block1')
        variable3 = Variable('var3', pipeline.dir_path, 'block2')
        variable4 = Variable('var4', pipeline.dir_path, 'block2')
        variable1.write_data('test')
        variable2.write_data(123)
        variable3.write_data([1, 2, 3, 4])
        variable4.write_data({'k1': 'v1', 'k2': 'v2'})
        self.assertEqual(variable1.read_data(), 'test')
        self.assertEqual(variable2.read_data(), 123)
        self.assertEqual(variable3.read_data(), [1, 2, 3, 4])
        self.assertEqual(variable4.read_data(), {'k1': 'v1', 'k2': 'v2'})

    def test_write_and_read_dataframe(self):
        pipeline = self.__create_pipeline('test pipeline 2')
        variable1 = Variable(
            'var1',
            pipeline.dir_path,
            'block1',
            variable_type=VariableType.DATAFRAME,
        )
        variable2 = Variable('var2', pipeline.dir_path, 'block2')
        df1 = pd.DataFrame(
            [
                [1, 'test'],
                [2, 'test2'],
            ],
            columns=['col1', 'col2']
        )
        df2 = pd.DataFrame(
            [
                [1, 'test', 3.123],
                [2, 'test2', 4.321],
            ],
            columns=['col1', 'col2', 'col3']
        )
        variable1.write_data(df1)
        variable2.write_data(df2)
        assert_frame_equal(variable1.read_data(), df1)
        assert_frame_equal(variable2.read_data(), df2)

    def test_write_and_read_dataframe_analysis(self):
        pipeline = self.__create_pipeline('test pipeline 3')
        variable = Variable(
            'var1',
            pipeline.dir_path,
            'block1',
            variable_type=VariableType.DATAFRAME_ANALYSIS,
        )
        data = dict(
            metadata=dict(
                column_types=dict(
                    col1='number',
                    col2='text',
                ),
            ),
            statistics=dict(
                count=100,
                count_distinct=50,
            ),
            insights=dict(),
            suggestions=[
                dict(
                    title='Remove outliers',
                )
            ]
        )
        variable.write_data(data)
        self.assertEquals(variable.read_data(), data)

    def __create_pipeline(self, name):
        pipeline = Pipeline.create(name, self.repo_path)
        block1 = Block.create('block1', 'data_loader', self.repo_path)
        block2 = Block.create('block2', 'transformer', self.repo_path)
        pipeline.add_block(block1)
        pipeline.add_block(block2)
        return pipeline