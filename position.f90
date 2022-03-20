module presenceMod
    use omp_lib
    implicit none
    contains

        subroutine presence (N, windowTimeLength, ts, rssi, scanner, numScanners, scannerList, place)
            integer,intent(in)         :: N, windowTimeLength, numScanners
            integer,intent(in)         :: rssi(N)
            integer(kind=8),intent(in) :: ts(N)
            integer,intent(in)         :: scanner(N), scannerList(numScanners)
            integer,intent(out)        :: place(N)
            integer                    :: i, j, idx
            integer                    :: freqScanner, maxScanner

            !$omp parallel do private(freqScanner, idx, maxScanner)
            do i=1,N
                call grabTheIndexWindowTimeLength(i, N, windowTimeLength, ts, idx)
                call mostFreqScanner (N, idx, i, scanner, numScanners, scannerList, freqScanner)
                call maxRssiScanner (N, idx, i, scanner, rssi, maxScanner)
                if ( maxScanner == freqScanner) then
                    place(i) = maxScanner
                else
                    place(i) = scannerList(1)
                end if
            end do
            !$omp end parallel do
        end subroutine presence

        subroutine maxRssiScanner (N, initIdx, endIdx, scanner, rssi, maxScanner)
            integer,intent(in)  :: N
            integer,intent(in)  :: rssi(0:N-1), initIdx, endIdx
            integer,intent(in)  :: scanner(0:N-1)
            integer,intent(out) :: maxScanner
            integer             :: maxRssi, maxRssiIdx, i

            maxRssi    = rssi(initIdx)
            maxRssiIdx = initIdx
            do i=initIdx+1,endIdx-1
                if ( rssi(i) > maxRssi ) then
                    maxRssi    = rssi(i)
                    maxRssiIdx = i
                end if
            end do
            maxScanner = scanner(maxRssiIdx)
        end subroutine maxRssiScanner

        subroutine mostFreqScanner (N, initIdx, endIdx, scanner, numScanners, scannerList, freqScanner)
            integer,intent(in)  :: initIdx, endIdx, numScanners, N
            integer,intent(in)  :: scanner(0:N-1), scannerList(numScanners)
            integer,intent(out) :: freqScanner
            integer             :: i, j, contagemScanners(numScanners), maior, maiorIdx
            integer             :: arrLen, strLen

            contagemScanners = 0
            do j=initIdx,endIdx-1
                do i=2,numScanners
                    if ( scanner(j) == scannerList(i) ) then
                        contagemScanners(i) = contagemScanners(i) + 1
                    end if
                end do
            end do

            maior = contagemScanners(1)
            maiorIdx = 1
            do i=2,numScanners
                if (contagemScanners(i) > maior) then
                    maior    = contagemScanners(i)
                    maiorIdx = i
                end if
            end do
            freqScanner = scannerList(maiorIdx)
        end subroutine mostFreqScanner

        subroutine grabTheIndexWindowTimeLength (idx, N, windowTimeLength, ts, initWindowIdx)
            integer,intent(in)         :: idx, windowTimeLength, N
            integer(kind=8),intent(in) :: ts(0:N-1)
            integer,intent(out)        :: initWindowIdx
            integer                    :: i
            logical                    :: key

            i = idx - 1
            if (i > 0) then
                if (ts(idx) - ts(i) >= windowTimeLength) then
                    key = .true.
                    initWindowIdx = i + 1
                else
                    key = .false.
                end if
                do while (key .eqv. .false.)
                    i = i - 1
                    if (ts(idx) - ts(i) >= windowTimeLength) then
                        initWindowIdx = i + 1
                        key = .true.
                    end if
                end do
            else
                initWindowIdx = i
            end if
        end subroutine grabTheIndexWindowTimeLength
end module presenceMod
