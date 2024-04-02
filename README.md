This is a project that I am currently working on. I started this project approximately in December 2023, and I've been working it on and off.

E-Callisto is an international network of solar radio spectrometers, which, similar to a standard radio receiver, constantly listen for radio signals. Unlike a radio, however, E-Callisto isn't created for man-made signals, but rather for naturally-occurring so-called "radio bursts". This collection of solar spectrometers collects gigabytes of data every single day, and over the course of the last several years, thousands of these solar events have been manually identified by hand. Manual data sorting is, however, not only inaccurate, but also extremely time-consuming and inefficient, so I have taken upon the task of automating this process.

This, however, does not come easy. The data is highly polluted by a large variety of both man-made signals and noise, making the creation of an accurate algorithm incredibly difficult. Using a combination of custom-tailored image de-noising techniques, traditional algorithms, statistical analysis methods, and, ultimately, AI, to achieve this feat, I have began to tackle this previously seemingly impossible task. Currently, I combine a simpler evaluation algorithm with a more complex convolutional neural network to achieve the most optimal results, however, our methods are still evolving. Eventually, I hope to not only make an accurate, but also fast and reliable algorithm for the detection of these solar events.

This project is not yet complete. As it stands, due to the lack of quality in the data, the model suffers greatly from overfitting, which makes getting quality results difficult. I am working on methods which aim at improving the collected data. Eventually, I hope to publish my findings in a journal.
