minV = -20.0
maxV = 30.0

def hsv2rgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b

def render(img):
    rowCount = img.shape[0]
    colCount = img.shape[1]
    newImg = np.zeros([rowCount, colCount, 3], dtype=np.uint8)
    for col in range(colCount):
        for row in range(rowCount):
            rawVal = img[row, col]
            if rawVal <= minV:
                dv = 0
            elif maxV <= rawVal:
                dv = 255
            else:
                dv = (rawVal - minV) / (maxV - minV) * 255
            # 255 -> 0, 0 -> 255
            r, g, b = hsv2rgb(255 - dv, 1.0, 1.0)
            newImg[row, col] = [b, g, r]
    return newImg

def getPolyData_U (originData, times):
    if times < 2 or times > 4:
        times = 2
    if 2 == times:
        x1 = originData[0][0]
        x2 = originData[0][1]
        y1 = originData[1][0]
        y2 = originData[1][1]
        coes = np.array([y1, (y2 - y1) / x2])
        return coes
    elif 3 == times:
        x1 = originData[0][0]
        x2 = originData[0][1]
        x3 = originData[0][2]
        y1 = originData[1][0]
        y2 = originData[1][1]
        y3 = originData[1][2]
        c2 = ((y3 - y1) * x2 - (y2 - y1) * x3) / (x2 *x3 *x3 - x2 * x2 * x3)
        coes = np.array([y1, (y2 - y1) / x2 - c2 * x2, c2])
        return coes
    elif 4 == times:
        x1 = originData[0][0]
        x2 = originData[0][1]
        x3 = originData[0][2]
        x4 = originData[0][3]
        y1 = originData[1][0]
        y2 = originData[1][1]
        y3 = originData[1][2]
        y4 = originData[1][3]
        c3 = ((y4 - y1) * x2 - (y2 - y1) * x4) / x2
        c3 -= ((y3 - y1) * x2 - (y2 - y1) * x3) / (x2 * x3 * x3 - x2 * x2 * x3) * (x2 * x4 * x4 - x2 * x2 * x4) / x2
        c3 /= x4 * x4 * x4 - x2 * x2 * x4 - (x2 * x3 * x3 * x3 - x2 * x2 * x2 * x3) / (x2 * x3 * x3 - x2 * x2 * x3) * (x4 * x4 - x2 * x4)
        c2 = ((y3 - y1) * x2 - (y2 - y1) * x3) / (x2 * x3 * x3 - x2 * x2 * x3)
        c2 -= c3 * ((x2 * x3 * x3 * x3 - x2 * x2 * x2 * x3) / (x2 * x3 * x3 - x2 * x2 * x3))
        c1 = ((y2 - y1) - c2 * x2 * x2 - c3 * x2 * x2 * x2) / x2
        coes = np.array([y1, c1, c2, c3])

def polynomialInterpolationArr (sourceDatas, dir, times):
    arrCount = len(sourceDatas)
    result = np.zeros(4 * arrCount, dtype=float)
    if 0 == dir:
        startIndex = 2
    else:
        startIndex = 1
    for i in range(arrCount):
        result[startIndex + 4 * i] = sourceDatas[i]
    originDatas = np.zeros((2, times), dtype=float)
    for i in range(arrCount - times + 1):
        for j in range(times):
            originDatas[0][j] = 4 * j
            originDatas[1][j] = sourceDatas[i + j]
        coes = getPolyData_U(originDatas, times)
        for j in range(1, 4):
            tempDou = coes[0] + j * coes[1]
            if 3 <= times:
                tempDou += j * j * coes[2]
            if 4 <= times:
                tempDou += j * j * j * coes[3]
            result[startIndex + 4 * i + j] = tempDou
    originDatas = np.zeros((2, 2), dtype=float)
    originDatas[1][0] = sourceDatas[0]
    originDatas[0][1] = 4
    originDatas[1][1] = sourceDatas[1]
    coes = getPolyData_U(originDatas, 2)
    if 0 == dir:
        result[1] = coes[0] - coes[1]
        result[0] = coes[0] - 2 * coes[1]
    else:
        result[0] = coes[0] - coes[1]
    for i in range(arrCount - times, arrCount - 1):
        for j in range(2):
            originDatas[0][j] = 4 * j
            originDatas[1][j] = sourceDatas[i + j]
        coes = getPolyData_U(originDatas, 2)
        for j in range(1, 4):
            result[startIndex + 4 * i + j] = coes[0] + j * coes[1]
    if 0 == dir:
        result[4 * arrCount - 1] = coes[0] + 5 * coes[1]
    else:
        result[4 * arrCount - 2] = coes[0] + 5 * coes[1]
        result[4 * arrCount - 1] = coes[0] + 6 * coes[1]
    return result

def doubleSize (img, dir, times):
    height = img.shape[0]
    width = img.shape[1]
    newImg = np.zeros([4 * height, 4 * width], dtype = float)
    for row in range(height):
        newImg[row, :] = polynomialInterpolationArr(img[row, :], dir, times)
    for col in range(4 * width):
        newImg[:, col] = polynomialInterpolationArr(newImg[:height, col], dir, times)
    return newImg

def generateImg (img):
    times = 2
    img2 = doubleSize(img, 0, times)
    img3 = doubleSize(img2, 1, times)
    finalImg = render(img3)
    return finalImg

