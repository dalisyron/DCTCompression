import scipy.fftpack
from numpy import r_
from skimage.io import imread, imsave
from skimage.color import rgb2ycbcr, ycbcr2rgb
import numpy as np


def dct2(a):
    return scipy.fftpack.dct(scipy.fftpack.dct(a, axis=0, norm='ortho'), axis=1, norm='ortho')


def idct2(a):
    return scipy.fftpack.idct(scipy.fftpack.idct(a, axis=0, norm='ortho'), axis=1, norm='ortho')


def dct8blocks(im):
    imsize = im.shape
    dct = np.zeros(imsize)

    # Do 8x8 DCT on image
    for i in r_[:imsize[0]:8]:
        for j in r_[:imsize[1]:8]:
            dct[i:(i + 8), j:(j + 8)] = dct2(im[i:(i + 8), j:(j + 8)])

    return dct


def idct8blocks(im):
    imsize = im.shape
    idct = np.zeros(imsize)

    # Do 8x8 DCT on image
    for i in r_[:imsize[0]:8]:
        for j in r_[:imsize[1]:8]:
            idct[i:(i + 8), j:(j + 8)] = idct2(im[i:(i + 8), j:(j + 8)])

    return idct


ijg_quantization_table = np.array(
    [[16, 11, 10, 16, 24, 40, 51, 61],
     [12, 12, 14, 19, 26, 58, 60, 55],
     [14, 13, 16, 24, 40, 57, 69, 56],
     [14, 17, 22, 29, 51, 87, 80, 62],
     [18, 22, 37, 56, 68, 109, 103, 77],
     [24, 35, 55, 64, 81, 104, 113, 92],
     [49, 64, 78, 87, 103, 121, 120, 101],
     [72, 92, 95, 98, 112, 100, 103, 99]]
)

masking_quantization_matrix = np.array(
    [[1, 1, 1, 1, 0, 0, 0, 0],
     [1, 1, 1, 0, 0, 0, 0, 0],
     [1, 1, 0, 0, 0, 0, 0, 0],
     [1, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0]]
)


def quantize8blocks(im, multiplier=1.0):
    imsize = im.shape
    quant = np.zeros(imsize)

    # Do 8x8 DCT on image
    for i in r_[:imsize[0]:8]:
        for j in r_[:imsize[1]:8]:
            quant[i:(i + 8), j:(j + 8)] = np.rint(
                np.multiply(im[i:(i + 8), j:(j + 8)], ((multiplier * 1.) / ijg_quantization_table)))
            # quant[i:(i + 8), j:(j + 8)] = im[i:(i + 8), j:(j + 8)] * masking_quantization_matrix

    return quant


def dequantize8blocks(im, multiplier=1.0):
    imsize = im.shape
    dequant = np.zeros(imsize)

    # Do 8x8 DCT on image
    for i in r_[:imsize[0]:8]:
        for j in r_[:imsize[1]:8]:
            dequant[i:(i + 8), j:(j + 8)] = np.multiply(im[i:(i + 8), j:(j + 8)],
                                                        (ijg_quantization_table / (multiplier * 1.)))

    return dequant


def ycbcr_channels(im):
    Y = 0
    Cb = 1
    Cr = 2
    return {
        "Y": im[:, :, Y],
        "Cb": im[:, :, Cb],
        "Cr": im[:, :, Cr]
    }


def compress_channel(im, multiplier=1.0):
    dct = dct8blocks(im)
    quant = quantize8blocks(dct, multiplier)
    dequant = dequantize8blocks(quant, multiplier)
    idct = idct8blocks(dequant)
    return idct


def join_ycbcr_channels(channels):
    Y = channels["Y"]
    Cb = channels["Cb"]
    Cr = channels["Cr"]
    shape = Y.shape
    array = np.zeros((shape[0], shape[1], 3))
    array[:, :, 0] = Y
    array[:, :, 1] = Cb
    array[:, :, 2] = Cr
    return array


def compress_channels(channels):
    compressed_channels = {}

    # Compress Y channel less since human eye is better at detecting changes in brightness compared to changes color
    for ch_name in channels:
        if ch_name == "Y":
            compressed_channels[ch_name] = compress_channel(channels[ch_name], 2)
        else:
            compressed_channels[ch_name] = compress_channel(channels[ch_name], 0.5)

    return compressed_channels


def compress(image_file, queue):
    im = rgb2ycbcr(imread(image_file)).astype(np.uint8)
    ch = ycbcr_channels(im)
    compressed_channels = compress_channels(ch)
    compressed_image = join_ycbcr_channels(compressed_channels)

    path = image_file.split('.')
    path[-2] += "_Compressed"
    compressed_path = ".".join(path)
    imsave(compressed_path, ycbcr2rgb(compressed_image))
    queue.put(compressed_path)
