from setuptools import setup
import setup_translate

pkg = 'Extensions.timFS'
setup(name='enigma2-plugin-extensions-timfs',
       version='3.0',
       description='timFS for Enigma2',
       package_dir={pkg: 'timFS'},
       packages=[pkg],
       package_data={pkg: ['skin/*.png', 'skin/*.xml', '*.png', 'locale/*/LC_MESSAGES/*.mo', '*.xml', 'groups']},
       cmdclass=setup_translate.cmdclass,  # for translation
      )
