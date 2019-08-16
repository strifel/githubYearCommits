def sortWithCount(elements):
    sortedElements = []
    for element in elements:
        if element not in elements or "count" not in elements[element]:
            continue
        if len(sortedElements) <= 0:
            sortedElements.append(elements[element])
        else:
            i = 0
            while True:
                if len(sortedElements) > i and sortedElements[i]['count'] < elements[element]['count']:
                    i += 1
                else:
                    break
            ii = len(sortedElements)
            sortedElements.append(True)
            while True:
                if ii == i:
                    break
                sortedElements[ii] = sortedElements[ii - 1]
                ii -= 1
            sortedElements[i] = elements[element]
    return sortedElements
